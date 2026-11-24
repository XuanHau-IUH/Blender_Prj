param(
    [string]$Type = 'execute_code',
    [string]$File,
    [string]$Code,
    [int]$Timeout = 25
)

$ErrorActionPreference = 'Stop'
$params = @{}
if ($File) { $Code = 'exec(compile(open(' + ($File | ConvertTo-Json -Compress) + ', encoding="utf-8").read(), ' + ($File | ConvertTo-Json -Compress) + ', "exec"), {"__name__": "__main__"})' }
if ($Code) { $params.code = $Code }
$request = @{ type=$Type; params=$params } | ConvertTo-Json -Depth 5 -Compress
$client = [System.Net.Sockets.TcpClient]::new()
try {
    $client.Connect('127.0.0.1', 9876)
    $stream = $client.GetStream()
    $stream.ReadTimeout = $Timeout * 1000
    $encoded = [Text.Encoding]::UTF8.GetBytes($request)
    $stream.Write($encoded, 0, $encoded.Length)
    $data = [System.IO.MemoryStream]::new()
    $buffer = [byte[]]::new(8192)
    $reply = $null
    while (($size = $stream.Read($buffer, 0, $buffer.Length)) -gt 0) {
        $data.Write($buffer, 0, $size)
        try { $reply = [Text.Encoding]::UTF8.GetString($data.ToArray()) | ConvertFrom-Json -ErrorAction Stop; break }
        catch { continue }
    }
    if (-not $reply) { throw 'Connection closed without a JSON response' }
    $reply | ConvertTo-Json -Depth 8
    if ($reply.status -ne 'success') { exit 1 }
} finally { $client.Dispose() }
