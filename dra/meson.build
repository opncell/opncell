project(
  'opncell-dra',
  'c',
  version: '0.1.0',
  meson_version: '>=0.63.0',
  default_options: [
    'c_std=c11',
    'warning_level=2',
  ]
)

inc = include_directories('src')

freeDiameter_proj = subproject(
  'freeDiameter',
  default_options: ['default_library=static'],
)

libfdcore_dep = freeDiameter_proj.get_variable('libfdcore_dep')

sources = files(
  'src/main.c',
  'src/dra-context.c',
  'src/provisioning.c',
)

executable(
  'opncell-drad',
  sources,
  include_directories: inc,
  dependencies: [libfdcore_dep],
  install: true,
  install_dir: get_option('sbindir'),
)
