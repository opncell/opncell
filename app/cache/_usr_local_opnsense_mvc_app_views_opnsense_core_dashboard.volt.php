

<?php $theme_name = (empty($ui_theme) ? ('opnsense') : ($ui_theme)); ?>
<!-- required for gridstack calculations -->
<link href="<?= view_cache_safe('/ui/css/gridstack.min.css') ?>" rel="stylesheet">
<!-- required for any amount of columns < 12 -->
<link href="<?= view_cache_safe('/ui/css/gridstack-extra.min.css') ?>" rel="stylesheet">
<!-- gridstack core -->
<script src="<?= view_cache_safe('/ui/js/gridstack-all.min.js') ?>"></script>
<script src="<?= view_cache_safe('/ui/js/opnsense_widget_manager.js') ?>"></script>
<script src="<?= view_cache_safe('/ui/js/moment-with-locales.min.js') ?>"></script>
<script src="<?= view_cache_safe('/ui/js/chart.min.js') ?>"></script>
<script src="<?= view_cache_safe('/ui/js/chartjs-plugin-streaming.min.js') ?>"></script>
<script src="<?= view_cache_safe('/ui/js/chartjs-plugin-colorschemes.js') ?>"></script>
<script src="<?= view_cache_safe('/ui/js/chartjs-adapter-moment.js') ?>"></script>
<script src="<?= view_cache_safe('/ui/js/smoothie.js') ?>"></script>
<link rel="stylesheet" type="text/css" href="<?= view_cache_safe(view_fetch_themed_filename('/css/dashboard.css', $theme_name)) ?>" rel="stylesheet" />

<script>
$( document ).ready(function() {
    let chartBackgroundColor = getComputedStyle(document.body).getPropertyValue('--chart-js-background-color').trim();
    let chartBorderColor = getComputedStyle(document.body).getPropertyValue('--chart-js-border-color').trim();
    let chartFontColor = getComputedStyle(document.body).getPropertyValue('--chart-js-font-color').trim();

    if (chartBackgroundColor) Chart.defaults.backgroundColor = chartBackgroundColor;
    if (chartBorderColor) Chart.defaults.borderColor = chartBorderColor;
    if (chartFontColor) Chart.defaults.color = chartFontColor;

    let widgetManager = new WidgetManager({
        float: false,
        columnOpts: {
            breakpoints: [{w: 500, c:1}, {w:900, c:3}, {w:9999, c:12}]
        },
        columns: 12,
        margin: 5,
        alwaysShowResizeHandle: false,
        sizeToContent: true,
        resizable: {
            handles: 'all'
        }
    }, {
        'save': "<?= $lang->_('Save') ?>",
        'ok': "<?= $lang->_('OK') ?>",
        'restore': "<?= $lang->_('Restore default layout') ?>",
        'restoreconfirm': "<?= $lang->_('Are you sure you want to restore the default widget layout?') ?>",
        'addwidget': "<?= $lang->_('Add Widget') ?>",
        'add': "<?= $lang->_('Add') ?>",
        'cancel': "<?= $lang->_('Cancel') ?>",
        'failed': "<?= $lang->_('Failed to load widget') ?>",
        'options': "<?= $lang->_('Options') ?>",
    });
    widgetManager.initialize();
});
</script>

<div class="grid-stack"></div>
