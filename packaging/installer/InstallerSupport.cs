using System.Diagnostics;

public static class InstallerSupport
{
    public static string ResolveCommand(string command)
    {
        if (Path.IsPathFullyQualified(command) && File.Exists(command))
        {
            return command;
        }

        var pathEntries = (Environment.GetEnvironmentVariable("PATH") ?? string.Empty)
            .Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries);
        var extensions = GetCommandExtensions(command);

        foreach (var directory in pathEntries)
        {
            foreach (var extension in extensions)
            {
                var candidate = Path.Combine(directory.Trim('"'), command + extension);
                if (File.Exists(candidate))
                {
                    return candidate;
                }
            }
        }

        return command;
    }

    public static void RunProcess(string fileName, string arguments, string workingDirectory, bool quiet = false)
    {
        var resolved = ResolveCommand(fileName);
        var startInfo = BuildStartInfo(resolved, arguments, workingDirectory, quiet);

        using var process = Process.Start(startInfo) ?? throw new InvalidOperationException($"Could not start {fileName}");
        process.WaitForExit();
        if (process.ExitCode != 0)
        {
            throw new InvalidOperationException($"{fileName} exited with code {process.ExitCode}");
        }
    }

    public static string EscapePowerShellSingleQuoted(string value)
    {
        return value.Replace("'", "''", StringComparison.Ordinal);
    }

    private static ProcessStartInfo BuildStartInfo(string resolvedCommand, string arguments, string workingDirectory, bool quiet)
    {
        var extension = Path.GetExtension(resolvedCommand);
        if (OperatingSystem.IsWindows() && (extension.Equals(".cmd", StringComparison.OrdinalIgnoreCase) || extension.Equals(".bat", StringComparison.OrdinalIgnoreCase)))
        {
            return new ProcessStartInfo
            {
                FileName = Path.Combine(Environment.SystemDirectory, "cmd.exe"),
                Arguments = $"/d /s /c \"\"{resolvedCommand}\" {arguments}\"",
                WorkingDirectory = workingDirectory,
                UseShellExecute = false,
                RedirectStandardOutput = quiet,
                RedirectStandardError = quiet
            };
        }

        return new ProcessStartInfo
        {
            FileName = resolvedCommand,
            Arguments = arguments,
            WorkingDirectory = workingDirectory,
            UseShellExecute = false,
            RedirectStandardOutput = quiet,
            RedirectStandardError = quiet
        };
    }

    private static string[] GetCommandExtensions(string command)
    {
        if (Path.HasExtension(command))
        {
            return [string.Empty];
        }

        if (!OperatingSystem.IsWindows())
        {
            return [string.Empty];
        }

        return (Environment.GetEnvironmentVariable("PATHEXT") ?? ".COM;.EXE;.BAT;.CMD")
            .Split(';', StringSplitOptions.RemoveEmptyEntries)
            .Append(string.Empty)
            .ToArray();
    }
}
