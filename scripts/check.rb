#!/usr/bin/env ruby
# Small source/build sanity check: Ruby standard library only, no network.
require 'yaml'
require 'date'
require 'uri'
require 'cgi'
require 'optparse'
options = { source_only: false, baseurl: nil }
OptionParser.new do |p|
  p.banner = 'Usage: ruby scripts/check.rb [--source-only] [--baseurl /repo] [output_dir]'
  p.on('--source-only') { options[:source_only] = true }
  p.on('--baseurl PATH') { |v| options[:baseurl] = v }
end.parse!
root = File.expand_path('..', __dir__)
errors = []
# Psych normally permits duplicate mapping keys. Check its syntax tree first.
check_mapping = lambda do |node, file|
  if node.is_a?(Psych::Nodes::Mapping)
    keys = node.children.each_slice(2).map { |k, _| k.respond_to?(:value) ? k.value : nil }
    keys.compact.tally.each { |key, n| errors << "#{file}: duplicate YAML key #{key.inspect}" if n > 1 }
  end
  Array(node.respond_to?(:children) ? node.children : []).each { |child| check_mapping.call(child, file) }
end
load_yaml = lambda do |text, file|
  check_mapping.call(Psych.parse_stream(text), file)
  value = YAML.safe_load(text, permitted_classes: [Date, Time], aliases: false) || {}
  errors << "#{file}: expected a YAML mapping" unless value.is_a?(Hash)
  value.is_a?(Hash) ? value : {}
rescue Psych::Exception => e
  errors << "#{file}: #{e.message}"
  {}
end
config = load_yaml.call(File.read(File.join(root, '_config.yml'), encoding: 'UTF-8'), '_config.yml')
yaml_files = Dir[File.join(root, '_data', '*.yml')] + Dir[File.join(root, '.github', 'workflows', '*.yml')]
data = yaml_files.to_h { |f| [File.basename(f, '.yml'), load_yaml.call(File.read(f, encoding: 'UTF-8'), f)] }
videos = data.fetch('videos', {})
frontpage = data.fetch('frontpage', {})
frontpage_title = frontpage.fetch('title', '').to_s.strip
home_title = frontpage_title.empty? ? config.fetch('title', '').to_s.strip : frontpage_title
home_title = 'Home' if home_title.empty?
if frontpage.key?('title') && !frontpage['title'].nil? && !frontpage['title'].is_a?(String)
  errors << 'frontpage.title must be text or an empty value'
end
local_asset = lambda do |value, context|
  next unless value.is_a?(String) && value.start_with?('/assets/', '/downloads/')
  path = value.split(/[?#]/, 2).first
  errors << "#{context}: missing local asset #{path}" unless File.file?(File.join(root, path.delete_prefix('/')))
end
walk_assets = lambda do |value, context|
  case value
  when Hash then value.each { |k, v| walk_assets.call(v, "#{context}.#{k}") }
  when Array then value.each { |v| walk_assets.call(v, context) }
  when String then local_asset.call(value, context)
  end
end
data.each { |key, value| walk_assets.call(value, key) }
uids = {}
%w[chapters papers].each do |collection|
  numbers = {}
  files = Dir[File.join(root, "_#{collection}", '*.md')]
  errors << "No documents in _#{collection}" if files.empty?
  files.each do |file|
    text = File.read(file, encoding: 'UTF-8')
    front = text.match(/\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n/m)
    unless front
      errors << "#{file}: missing YAML front matter"
      next
    end
    metadata = load_yaml.call(front[1], file)
    %w[title uid].each { |key| errors << "#{file}: missing #{key}" if metadata[key].to_s.strip.empty? }
    uid = metadata['uid']
    errors << "#{file}: duplicate uid #{uid}" if uids.key?(uid)
    uids[uid] = file
    order_key = collection == 'chapters' ? 'chapter_number' : 'order'
    number = metadata[order_key]
    errors << "#{file}: #{order_key} must be a positive integer" unless number.is_a?(Integer) && number.positive?
    errors << "#{file}: duplicate #{order_key} #{number}" if numbers.key?(number)
    numbers[number] = file
    media_keys = %w[videos comparison_videos additional_videos].flat_map { |key| Array(metadata[key]) }
    media_keys += text.scan(/{%\s*include\s+video\.html\s+key=["']([^"']+)["']/).flatten
    # Direct grouped includes accept comma-separated keys, including a single key.
    media_keys += text.scan(/{%\s*include\s+video-group\.html\s+[^%]*?keys=["']([^"']*)["']/m).flatten.flat_map { |keys| keys.split(',').map(&:strip) }
    media_keys.reject!(&:empty?)
    media_keys.uniq.each { |key| errors << "#{file}: unknown video key #{key}" unless videos.key?(key) }
    walk_assets.call(metadata, file)
    text.scan(/(?:src|poster|link)=["']([^"']+)["']/).flatten.each { |v| local_asset.call(v, file) }
  end
end
videos.each do |key, video|
  unless video.is_a?(Hash)
    errors << "videos.#{key}: expected a mapping"
    next
  end
  %w[number].each { |field| errors << "videos.#{key}: missing #{field}" if video[field].to_s.strip.empty? }
  # Titles, descriptions, and captions may intentionally be empty. Never invent them.
  %w[title caption].each do |field|
    value = video[field]
    errors << "videos.#{key}.#{field}: expected text or an empty value" unless value.nil? || value.is_a?(String)
  end
  %w[src poster download archive track transcript].each do |field|
    value = video[field].to_s.strip
    next if value.empty? || value.start_with?('/', 'https://', 'http://')
    errors << "videos.#{key}.#{field}: use /local/path or an HTTP(S) URL"
  end
end
unless options[:source_only]
  output = File.expand_path(ARGV[0] || '_site', root)
  base = (options[:baseurl] || config['baseurl'] || '').sub(%r{/$}, '')
  errors << "#{output}: chapter-template must not be published" if File.exist?(File.join(output, 'chapter-template.html'))
  errors << "#{output}: placeholder assets must not be published" if File.exist?(File.join(output, 'assets', 'placeholders'))
  pages = Dir[File.join(output, '**', '*.html')]
  errors << "No HTML found in #{output}; build Jekyll first" if pages.empty?
  # The project's templates use quoted attributes. Not a full HTML parser.
  html = pages.to_h { |path| [path, File.read(path, encoding: 'UTF-8')] }
  homepage = html[File.join(output, 'index.html')]
  if homepage
    heading = homepage.match(/<h1\b[^>]*\bid=["']home-title["'][^>]*>(.*?)<\/h1>/m)
    tab_title = homepage.match(/<title>(.*?)<\/title>/m)
    errors << 'index.html: home heading does not match frontpage.title (or its fallback)' unless heading && CGI.unescapeHTML(heading[1]).strip == home_title
    errors << 'index.html: browser-tab title does not match frontpage.title (or its fallback)' unless tab_title && CGI.unescapeHTML(tab_title[1]).strip == home_title
  else
    errors << 'Missing generated home page index.html'
  end
  ids = html.transform_values { |text| text.scan(/\bid=["']([^"']+)["']/).flatten }
  ids.each { |path, list| list.tally.each { |id, n| errors << "#{path}: duplicate HTML id #{id}" if n > 1 } }
  html.each do |path, text|
    # BibTeX may legitimately contain doubled braces inside a code block.
    markup = text.gsub(/<pre\b[^>]*>.*?<\/pre>/m, '')
    errors << "#{path}: unresolved Liquid tag" if markup.match?(/\{%|\{\{/)
    errors << "#{path}: unknown media key" if text.include?('Unknown video key:')
    errors << "#{path}: temporary content remains" if text.match?(%r{\[.*?PLACEHOLDER.*?\]|/assets/placeholders/|/downloads/placeholder-notes\.txt|data-video-placeholder|class=["']preview-notice}i)
    text.scan(/\b(href|src|poster)=["']([^"']*)["']/).each do |attribute, raw|
      value = CGI.unescapeHTML(raw)
      if value.empty?
        errors << "#{path}: empty #{attribute}"
        next
      end
      next if value.match?(%r{\A(?:https?:|mailto:|tel:|data:|//)}i)
      if value.match?(/\A[a-z][a-z0-9+.-]*:/i)
        errors << "#{path}: unsupported URL scheme #{value}"
        next
      end
      address, fragment = value.split('#', 2)
      address = URI::DEFAULT_PARSER.unescape(address.split('?', 2).first.to_s)
      if address.empty?
        target = path
      elsif address.start_with?('/')
        unless base.empty? || address == base || address.start_with?(base + '/')
          errors << "#{path}: #{value} ignores baseurl #{base}"
          next
        end
        relative = base.empty? ? address : address.delete_prefix(base)
        target = File.join(output, relative.delete_prefix('/'))
      else
        target = File.expand_path(address, File.dirname(path))
      end
      target = File.join(target, 'index.html') if File.directory?(target)
      unless File.file?(target)
        errors << "#{path}: missing link/resource #{value}"
        next
      end
      if fragment && !fragment.empty? && ids.key?(target)
        decoded = URI::DEFAULT_PARSER.unescape(fragment)
        errors << "#{path}: missing fragment ##{fragment}" unless ids[target].include?(decoded)
      end
    end
  end
end
if errors.any?
  warn errors.uniq.join("\n")
  abort "FAILED: #{errors.uniq.length} issue(s)."
end
puts "PASS: source metadata and local assets#{options[:source_only] ? '' : ', rendered pages, internal links, fragments, and baseurl'}."
