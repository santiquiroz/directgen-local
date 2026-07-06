var npm = InstallerSupport.ResolveCommand("npm");

if (OperatingSystem.IsWindows() && !npm.EndsWith("npm.cmd", StringComparison.OrdinalIgnoreCase))
{
    throw new Exception($"Expected npm.cmd on Windows, got {npm}");
}

InstallerSupport.RunProcess("npm", "--version", Directory.GetCurrentDirectory(), quiet: true);

var temp = Path.Combine(Path.GetTempPath(), "DirectGenLocalInstallerTests", Guid.NewGuid().ToString("N"));
var installDir = Path.Combine(temp, "install");
var backupDir = Path.Combine(temp, "backup");
Directory.CreateDirectory(Path.Combine(installDir, "data", "models"));
File.WriteAllText(Path.Combine(installDir, "data", "models", "model.txt"), "keep");
InstallerSupport.BackupDataDirectory(installDir, backupDir);
Directory.Delete(installDir, recursive: true);
Directory.CreateDirectory(installDir);
InstallerSupport.RestoreDataDirectory(installDir, backupDir);
if (File.ReadAllText(Path.Combine(installDir, "data", "models", "model.txt")) != "keep")
{
    throw new Exception("Installer data backup/restore failed.");
}

var escaped = InstallerSupport.EscapePowerShellSingleQuoted(@"C:\Users\santi\AppData\Local\DirectGenLocal's");
if (escaped != @"C:\Users\santi\AppData\Local\DirectGenLocal''s")
{
    throw new Exception($"Unexpected PowerShell escape result: {escaped}");
}

Console.WriteLine("Installer support tests passed.");
