project(
  'opncell-dra',
  'c',
  version: '0.1.0',
  meson_version: '>=0.60.0',
  default_options: [
    'c_std=c11',
    'warning_level=2',
  ]
)

inc = include_directories('src')

sources = files(
  'src/main.c',
  'src/dra-context.c',
  'src/provisioning.c',
)

executable(
  'opncell-drad',
  sources,
  include_directories: inc,
  install: true,
  install_dir: get_option('sbindir'),
)
