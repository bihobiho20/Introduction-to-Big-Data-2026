# Render measured curves with the Windows .NET charting library, no downloads.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms.DataVisualization
Add-Type -AssemblyName System.Drawing

function New-ResultChart([string]$Title, [string]$XTitle, [string]$YTitle) {
    $chart = New-Object System.Windows.Forms.DataVisualization.Charting.Chart
    $chart.Width = 1100
    $chart.Height = 640
    $chart.BackColor = [System.Drawing.Color]::White
    $chart.Font = New-Object System.Drawing.Font('Segoe UI', 12)
    $area = New-Object System.Windows.Forms.DataVisualization.Charting.ChartArea('data')
    $area.AxisX.Title = $XTitle
    $area.AxisY.Title = $YTitle
    $area.AxisX.Interval = 1
    $area.AxisX.MajorGrid.Enabled = $false
    $area.AxisY.MajorGrid.LineColor = [System.Drawing.Color]::Gainsboro
    $chart.ChartAreas.Add($area)
    $heading = $chart.Titles.Add($Title)
    $heading.Font = New-Object System.Drawing.Font('Segoe UI', 17, [System.Drawing.FontStyle]::Bold)
    $legend = New-Object System.Windows.Forms.DataVisualization.Charting.Legend
    $legend.Docking = 'Bottom'
    $chart.Legends.Add($legend)
    return $chart
}

function Add-Line($Chart, [string]$Name, [string]$Color) {
    $series = New-Object System.Windows.Forms.DataVisualization.Charting.Series($Name)
    $series.ChartType = 'Line'
    $series.BorderWidth = 3
    $series.Color = [System.Drawing.ColorTranslator]::FromHtml($Color)
    $series.MarkerStyle = 'Circle'
    $series.MarkerSize = 8
    $series.IsValueShownAsLabel = $true
    $series.LabelFormat = 'N0'
    $series.IsXValueIndexed = $true
    $Chart.Series.Add($series)
    return $series
}

$outDir = Join-Path $PSScriptRoot 'out'
$explosion = Get-Content -Raw -Encoding UTF8 (Join-Path $outDir 'explosion.json') | ConvertFrom-Json
$chart = New-ResultChart 'A-Priori: counters needed vs. answers found' 'Support (decreasing; categorical spacing)' 'Count (log scale)'
$chart.ChartAreas[0].AxisY.IsLogarithmic = $true
$chart.ChartAreas[0].AxisY.Minimum = 100
$chart.ChartAreas[0].AxisY.Maximum = 10000000
$chart.ChartAreas[0].AxisY.LabelStyle.Format = 'N0'
$counters = Add-Line $chart 'Peak pair counters' '#2563eb'
$answers = Add-Line $chart 'Frequent pairs' '#d97706'
foreach ($row in $explosion.runs) {
    [void]$counters.Points.AddXY([string]$row.support, [double]$row.peak_counters)
    [void]$answers.Points.AddXY([string]$row.support, [double]$row.frequent_pairs)
}
$chart.SaveImage((Join-Path $outDir 'explosion.png'), 'Png')
$chart.Dispose()

$memory = Get-Content -Raw -Encoding UTF8 (Join-Path $outDir 'pcy_memory.json') | ConvertFrom-Json
$chart = New-ResultChart 'Memory crossover: support 50, 2,097,152 PCY buckets' 'Baskets (prefix of the same seeded data; categorical spacing)' 'Peak traced Python allocations (MB, decimal)'
$chart.ChartAreas[0].AxisY.Minimum = 0
$base = Add-Line $chart 'Plain A-Priori' '#2563eb'
$pcy = Add-Line $chart 'PCY' '#d97706'
$base.LabelFormat = 'N2'
$pcy.LabelFormat = 'N2'
foreach ($row in $memory.crossover) {
    [void]$base.Points.AddXY([string]$row.baskets, $row.baseline.peak_bytes / 1e6)
    [void]$pcy.Points.AddXY([string]$row.baskets, $row.pcy.peak_bytes / 1e6)
}
$chart.SaveImage((Join-Path $outDir 'pcy_memory.png'), 'Png')
$chart.Dispose()
Write-Output 'Saved out/explosion.png and out/pcy_memory.png'

$stressPath = Join-Path $outDir 'stress.json'
if (Test-Path -LiteralPath $stressPath) {
    $stress = Get-Content -Raw -Encoding UTF8 $stressPath | ConvertFrom-Json
    $chart = New-ResultChart 'Larger data: measured memory and declared budget' 'Support (decreasing; categorical spacing)' 'Peak traced Python allocations (MiB; input excluded)'
    $subtitle = $chart.Titles.Add('100,000 baskets, 20,000 items; last run completed above budget')
    $subtitle.Font = New-Object System.Drawing.Font('Segoe UI', 11)
    $chart.ChartAreas[0].AxisY.Minimum = 0
    $peak = Add-Line $chart 'Measured peak' '#2563eb'
    $limit = Add-Line $chart 'Declared budget (1 GiB)' '#dc2626'
    $peak.LabelFormat = 'N2'
    $limit.IsValueShownAsLabel = $false
    $limit.BorderDashStyle = 'Dash'
    $limit.MarkerStyle = 'None'
    foreach ($row in $stress.runs) {
        [void]$peak.Points.AddXY([string]$row.support, $row.peak_bytes / 1MB)
        [void]$limit.Points.AddXY([string]$row.support, $stress.budget.peak_python_bytes / 1MB)
    }
    $last = $peak.Points[$peak.Points.Count - 1]
    $last.Color = [System.Drawing.Color]::Red
    $last.MarkerStyle = 'Cross'
    $last.MarkerSize = 12
    $chart.SaveImage((Join-Path $outDir 'stress.png'), 'Png')
    $chart.Dispose()
    Write-Output 'Saved out/stress.png'
}
