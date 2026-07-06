using System.Diagnostics;
using System.IO.Compression;
using System.Runtime.InteropServices;

const string Owner = "santiquiroz";
const string Repo = "directgen-local";
const string Version = "v0.1.5";

AppDomain.CurrentDomain.UnhandledException += (_, eventArgs) =>
{
    Console.Error.WriteLine(eventArgs.ExceptionObject);
    PromptBeforeClose();
};

var installDir = Path.Combine(
    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
    "DirectGenLocal"
);
var tempRoot = Path.Combine(Path.GetTempPath(), "DirectGenLocalInstaller");
var zipPath = Path.Combine(tempRoot, $"{Version}.zip");
var downloadUrl = $"https://github.com/{Owner}/{Repo}/archive/refs/tags/{Version}.zip";

Console.WriteLine("DirectGen Local installer");
Console.WriteLine($"Version: {Version}");
Console.WriteLine($"Install path: {installDir}");

RequireWindows();
RequireCommand("python", "Python 3.11+ no esta disponible en PATH.");
RequireCommand("node", "Node.js no esta disponible en PATH.");
RequireCommand("npm", "npm no esta disponible en PATH.");

Directory.CreateDirectory(tempRoot);
if (Directory.Exists(installDir))
{
    Console.WriteLine("Removing previous installation...");
    StopExistingInstall(installDir);
    DeleteDirectoryWithRetries(installDir);
}

Console.WriteLine("Downloading release source...");
using (var http = new HttpClient())
{
    http.DefaultRequestHeaders.UserAgent.ParseAdd("DirectGenLocalInstaller/0.1.0");
    await using var input = await http.GetStreamAsync(downloadUrl);
    await using var output = File.Create(zipPath);
    await input.CopyToAsync(output);
}

Console.WriteLine("Extracting...");
ZipFile.ExtractToDirectory(zipPath, tempRoot, overwriteFiles: true);
var extracted = Directory.GetDirectories(tempRoot, $"{Repo}-{Version.TrimStart('v')}").FirstOrDefault()
    ?? Directory.GetDirectories(tempRoot).First(path => Path.GetFileName(path).StartsWith($"{Repo}-"));
CopyDirectory(extracted, installDir);

Console.WriteLine("Installing API dependencies...");
RunPowerShell(installDir, Path.Combine(installDir, "scripts", "setup-api.ps1"));

Console.WriteLine("Installing web dependencies...");
RunProcess("npm", "install", Path.Combine(installDir, "apps", "web"));

var launcher = Path.Combine(installDir, "DirectGenLocal.cmd");
File.WriteAllText(
    launcher,
    $"""
    @echo off
    cd /d "{installDir}"
    powershell -NoProfile -ExecutionPolicy Bypass -File "{Path.Combine(installDir, "scripts", "start-all.ps1")}"
    """
);

CreateShortcut(launcher);

Console.WriteLine();
Console.WriteLine("Installation complete.");
Console.WriteLine("DirectML dependencies are optional and heavy.");
Console.WriteLine($"Run this when ready: powershell -NoProfile -ExecutionPolicy Bypass -File \"{Path.Combine(installDir, "scripts", "setup-directml.ps1")}\"");
Console.WriteLine($"Start app: {launcher}");

static void RequireWindows()
{
    if (!RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
    {
        throw new InvalidOperationException("This installer is for Windows only.");
    }
}

static void RequireCommand(string command, string errorMessage)
{
    try
    {
        RunProcess(command, "--version", Directory.GetCurrentDirectory(), quiet: true);
    }
    catch
    {
        throw new InvalidOperationException(errorMessage);
    }
}

static void RunPowerShell(string workingDirectory, string scriptPath)
{
    RunProcess(
        "powershell",
        $"-NoProfile -ExecutionPolicy Bypass -File \"{scriptPath}\"",
        workingDirectory
    );
}

static void RunProcess(string fileName, string arguments, string workingDirectory, bool quiet = false)
{
    InstallerSupport.RunProcess(fileName, arguments, workingDirectory, quiet);
}

static void CopyDirectory(string source, string destination)
{
    Directory.CreateDirectory(destination);
    foreach (var directory in Directory.GetDirectories(source, "*", SearchOption.AllDirectories))
    {
        Directory.CreateDirectory(directory.Replace(source, destination));
    }

    foreach (var file in Directory.GetFiles(source, "*", SearchOption.AllDirectories))
    {
        var target = file.Replace(source, destination);
        File.Copy(file, target, overwrite: true);
    }
}

static void StopExistingInstall(string installDir)
{
    var escapedInstallDir = InstallerSupport.EscapePowerShellSingleQuoted(installDir);
    var script =
        "$root = '" + escapedInstallDir + "'; " +
        "$all = @(Get-CimInstance Win32_Process); " +
        "$pids = @(); " +
        "$pids += $all | Where-Object { $_.CommandLine -and $_.CommandLine -like ('*' + $root + '*') } | Select-Object -ExpandProperty ProcessId; " +
        "$pids += Get-NetTCPConnection -LocalPort 8000,5173 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; " +
        "for ($i = 0; $i -lt 5; $i++) { " +
        "  $children = $all | Where-Object { $pids -contains $_.ParentProcessId } | Select-Object -ExpandProperty ProcessId; " +
        "  $pids = @($pids + $children | Select-Object -Unique); " +
        "} " +
        "$pids | Where-Object { $_ -and $_ -ne $PID } | Sort-Object -Descending | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }";
    RunProcess("powershell", $"-NoProfile -ExecutionPolicy Bypass -Command \"{script}\"", Directory.GetCurrentDirectory(), quiet: true);
    Thread.Sleep(1500);
}

static void DeleteDirectoryWithRetries(string directory)
{
    for (var attempt = 1; attempt <= 8; attempt++)
    {
        try
        {
            Directory.Delete(directory, recursive: true);
            return;
        }
        catch (IOException) when (attempt < 8)
        {
            Thread.Sleep(750);
        }
        catch (UnauthorizedAccessException) when (attempt < 8)
        {
            Thread.Sleep(750);
        }
    }

    Directory.Delete(directory, recursive: true);
}

static void CreateShortcut(string launcher)
{
    var desktop = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
    var shortcutPath = Path.Combine(desktop, "DirectGen Local.lnk");
    var command = $"""
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut('{shortcutPath}')
    $shortcut.TargetPath = '{launcher}'
    $shortcut.WorkingDirectory = '{Path.GetDirectoryName(launcher)}'
    $shortcut.Save()
    """;
    RunProcess("powershell", $"-NoProfile -Command \"{command}\"", Directory.GetCurrentDirectory(), quiet: true);
}

static void PromptBeforeClose()
{
    if (Environment.UserInteractive)
    {
        Console.WriteLine("Press Enter to close.");
        Console.ReadLine();
    }
}
