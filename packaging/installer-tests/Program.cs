var npm = InstallerSupport.ResolveCommand("npm");

if (OperatingSystem.IsWindows() && !npm.EndsWith("npm.cmd", StringComparison.OrdinalIgnoreCase))
{
    throw new Exception($"Expected npm.cmd on Windows, got {npm}");
}

InstallerSupport.RunProcess("npm", "--version", Directory.GetCurrentDirectory(), quiet: true);
Console.WriteLine("Installer support tests passed.");
