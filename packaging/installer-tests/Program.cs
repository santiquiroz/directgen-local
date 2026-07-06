var npm = InstallerSupport.ResolveCommand("npm");

if (OperatingSystem.IsWindows() && !npm.EndsWith("npm.cmd", StringComparison.OrdinalIgnoreCase))
{
    throw new Exception($"Expected npm.cmd on Windows, got {npm}");
}

InstallerSupport.RunProcess("npm", "--version", Directory.GetCurrentDirectory(), quiet: true);

var escaped = InstallerSupport.EscapePowerShellSingleQuoted(@"C:\Users\santi\AppData\Local\DirectGenLocal's");
if (escaped != @"C:\Users\santi\AppData\Local\DirectGenLocal''s")
{
    throw new Exception($"Unexpected PowerShell escape result: {escaped}");
}

Console.WriteLine("Installer support tests passed.");
