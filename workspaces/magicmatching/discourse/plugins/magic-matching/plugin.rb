# frozen_string_literal: true
# name: magic-matching
# about: A plugin to interact with magic-matching API
# version: 0.0.1
# authors: CNG
# url: https://github.com/cngarrison/discourse-plugin-magic-matching

enabled_site_setting :magicmatching_enabled

add_admin_route 'magic_matching.title', 'magic-matching'

Discourse::Application.routes.append do
  get '/admin/plugins/magic-matching' => 'admin/plugins#index', constraints: StaffConstraint.new
end


after_initialize do

  %w[
    ../lib/magicmatching_events_handlers.rb
  ].each do |path|
    load File.expand_path(path, __FILE__)
  end


  STDERR.puts '-----------------------------------------------------'
  STDERR.puts 'MagicMatching is ready, say "Match Me!" on Discourse!'
  STDERR.puts '-----------------------------------------------------'
  STDERR.puts '(--------      If not check logs          ----------)'
end
