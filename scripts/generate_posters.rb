#!/usr/bin/env ruby
# Extract the actual first decoded frame, once per distinct video source.
# Ruby standard library + FFmpeg only. No changes to _data/videos.yml.
require 'yaml'
require 'json'
require 'digest'
require 'fileutils'
require 'open3'
require 'optparse'
require 'timeout'
require 'uri'
require 'time'

root = File.expand_path('..', __dir__)
options = {
  root: root, input: nil, local_dir: nil, force: false,
  timeout: 90, width: 1280, only: [], dry_run: false
}
OptionParser.new do |p|
  p.banner = 'Usage: ruby scripts/generate_posters.rb [options]'
  p.on('--root DIR', 'Website root (default: parent of scripts/)') { |v| options[:root] = File.expand_path(v) }
  p.on('--input FILE', 'Alternative video YAML file (for testing)') { |v| options[:input] = File.expand_path(v) }
  p.on('--local-dir DIR', 'Use local MP4 files with the same basenames instead of remote URLs') { |v| options[:local_dir] = File.expand_path(v) }
  p.on('--only KEY', 'Process only this video key; repeat to select several') { |v| options[:only] << v }
  p.on('--force', 'Re-extract existing posters') { options[:force] = true }
  p.on('--timeout SECONDS', Integer, 'Time limit per source (default: 90)') { |v| options[:timeout] = v }
  p.on('--width PIXELS', Integer, 'Maximum poster width (default: 1280; no upscaling)') { |v| options[:width] = v }
  p.on('--dry-run', 'List the sources without downloading or writing files') { options[:dry_run] = true }
  p.on('-h', '--help', 'Show this help') { puts p; exit }
end.parse!
abort 'Width and timeout must be positive.' unless options[:width].positive? && options[:timeout].positive?
root = options[:root]
input = options[:input] || File.join(root, '_data', 'videos.yml')
abort "Missing video data: #{input}" unless File.file?(input)
begin
  videos = YAML.safe_load(File.read(input, encoding: 'UTF-8'), aliases: false) || {}
rescue Psych::Exception => e
  abort "Invalid video YAML: #{e.message}"
end
abort 'The video data must be a YAML mapping.' unless videos.is_a?(Hash)
unknown = options[:only] - videos.keys
abort "Unknown video keys: #{unknown.join(', ')}" unless unknown.empty?
selected = videos.select { |key, value| value.is_a?(Hash) && !value['src'].to_s.strip.empty? && (options[:only].empty? || options[:only].include?(key)) }
groups = selected.group_by { |_, video| video['src'].to_s.strip }
puts "#{selected.length} video entries; #{groups.length} distinct sources."
if options[:dry_run]
  groups.each { |src, entries| puts "#{entries.map(&:first).join(', ')}\n  #{src}" }
  exit
end
begin
  _, ffmpeg_status = Open3.capture2e('ffmpeg', '-version')
  abort 'FFmpeg could not start.' unless ffmpeg_status.success?
rescue Errno::ENOENT
  abort 'FFmpeg is not installed. On macOS with Homebrew, run: brew install ffmpeg'
end

poster_dir = File.join(root, 'assets', 'posters')
manifest_file = File.join(root, '_data', 'video_posters.yml')
report_file = File.join(root, 'docs', 'poster-generation.json')
FileUtils.mkdir_p(poster_dir)
FileUtils.mkdir_p(File.dirname(manifest_file))
FileUtils.mkdir_p(File.dirname(report_file))
manifest = File.file?(manifest_file) ? YAML.safe_load(File.read(manifest_file), aliases: false) : {}
manifest = {} unless manifest.is_a?(Hash)
report = { 'generated_at' => Time.now.utc.iso8601, 'entries' => selected.length, 'distinct_sources' => groups.length, 'results' => [] }

# Spawn as a process group so timeout cleanup also stops FFmpeg's children.
def run_ffmpeg(command, seconds)
  output = ''
  status = nil
  Open3.popen2e(*command, pgroup: true) do |stdin, combined, wait|
    stdin.close
    reader = Thread.new { combined.read }
    begin
      Timeout.timeout(seconds) do
        output = reader.value
        status = wait.value
      end
    rescue Timeout::Error
      begin
        Process.kill('TERM', -wait.pid)
        Timeout.timeout(3) { wait.value }
      rescue Errno::ESRCH
        # Already stopped.
      rescue Timeout::Error
        Process.kill('KILL', -wait.pid) rescue nil
        wait.value
      end
      output = reader.value
      raise "FFmpeg exceeded #{seconds}s. #{output[-1200, 1200] || output}"
    ensure
      reader.join
    end
  end
  raise "FFmpeg failed: #{output[-1800, 1800] || output}" unless status&.success?
end

groups.each_with_index do |(src, entries), index|
  keys = entries.map(&:first)
  filename = "video-#{Digest::SHA256.hexdigest(src)[0, 16]}.jpg"
  destination = File.join(poster_dir, filename)
  temporary = File.join(poster_dir, ".#{filename}.tmp.jpg")
  result = { 'keys' => keys, 'src' => src, 'poster' => "/assets/posters/#{filename}" }
  begin
    if !options[:force] && File.file?(destination) && File.size(destination).positive?
      result['status'] = 'reused'
    else
      source = if options[:local_dir]
                 basename = File.basename(URI::DEFAULT_PARSER.unescape(URI.parse(src).path))
                 File.join(options[:local_dir], basename)
               elsif src.match?(%r{\Ahttps?://}i)
                 src
               else
                 File.join(root, src.delete_prefix('/'))
               end
      if !source.match?(%r{\Ahttps?://}i) && !File.file?(source)
        raise "Local video not found: #{source}"
      end
      command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y']
      if source.match?(%r{\Ahttps?://}i)
        command += ['-rw_timeout', (options[:timeout] * 1_000_000).to_s]
      end
      # Do not seek forward: this is the first frame, even when the first frame is black.
      command += ['-i', source, '-map', '0:v:0', '-frames:v', '1', '-an', '-sn', '-dn',
                  '-vf', "scale='min(#{options[:width]},iw)':-2", '-q:v', '2', '-threads', '1', temporary]
      run_ffmpeg(command, options[:timeout])
      raise 'FFmpeg produced no JPEG.' unless File.file?(temporary) && File.size(temporary).positive?
      raise 'The output is not a JPEG.' unless File.binread(temporary, 2) == "\xFF\xD8".b
      File.rename(temporary, destination)
      result['status'] = 'generated'
    end
    result['bytes'] = File.size(destination)
    keys.each { |key| manifest[key] = { 'src' => src, 'poster' => result['poster'] } }
    puts "[#{index + 1}/#{groups.length}] #{result['status']}: #{filename} (#{keys.join(', ')})"
  rescue StandardError => e
    result['status'] = 'failed'
    result['error'] = e.message
    warn "[#{index + 1}/#{groups.length}] FAILED: #{src}\n  #{e.message}"
  ensure
    FileUtils.rm_f(temporary)
    report['results'] << result
  end
end
# Only successful files are added; failed requests never create fake or broken posters.
manifest_temp = "#{manifest_file}.tmp"
File.write(manifest_temp, manifest.to_yaml)
File.rename(manifest_temp, manifest_file)
File.write(report_file, JSON.pretty_generate(report) + "\n")
failures = report['results'].count { |result| result['status'] == 'failed' }
puts "Posters: #{groups.length - failures}/#{groups.length} distinct sources available."
puts "Manifest: #{manifest_file}\nReport: #{report_file}"
puts 'Rebuild Jekyll to use the generated local posters.'
exit(failures.zero? ? 0 : 1)
