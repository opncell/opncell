<script>
// Extend only the Cellular log grid; keep the platform partial unchanged.
const opncellOriginalLogGrid = $.fn.UIBootgrid;
$.fn.UIBootgrid = function (settings) {
    if (this.is('#grid-log') && settings && settings.search === '/api/diagnostics/log/opncell/{{scope}}') {
        settings.options = settings.options || {};
        settings.options.rowCount = [50, 100, 200, 500, 1000, 5000, -1];
    }
    return opncellOriginalLogGrid.apply(this, arguments);
};
// Register before the platform partial creates its grid and initial request.
$(function () {
    // Add before the platform grid restores its saved timeframe selection.
    const timeframe = $("#validFrom_filter");
    timeframe.find('option[value="all"]').text("{{ lang._('All') }}");
    if (!timeframe.find('option[value="hour"]').length) {
        timeframe.prepend($('<option value="hour"></option>').text("{{ lang._('Last hour') }}"));
    }
    // The styled picker can already be initialized before document-ready.
    // Refresh its option cache as well as the underlying select element.
    if (timeframe.data("selectpicker")) { timeframe.selectpicker("refresh"); }
});
$.ajaxPrefilter(function (options) {
    const cellularLog = options.url.indexOf('/api/diagnostics/log/opncell/') !== -1;
    if (cellularLog && $("#validFrom_filter").val() === "hour") {
        // The platform request handler only knows day/week/month.
        const params = new URLSearchParams(options.data || "");
        params.set("validFrom", Math.floor(Date.now() / 1000) - 3600);
        options.data = params.toString();
    }
    options.url = options.url.replace('/api/diagnostics/log/opncell/', '/api/opncell/log/query/');
});
</script>
<p><a href="/ui/opncell/log">{{ lang._('Active daemon logs') }}</a></p>
{{ partial("OPNsense/Diagnostics/log") }}

<div id="opncell_log_refresh" class="btn-group">
    <button id="opncell_log_refresh_toggle" type="button" class="btn btn-default" aria-pressed="false">
        <span class="fa fa-refresh" aria-hidden="true"></span> {{ lang._('Auto refresh') }}
    </button>
</div>

<div id="opncell_log_path" class="text-muted" style="padding: 7px 12px 7px 0; overflow-wrap: anywhere;">
    {{ lang._('Log file') }}: <code>{{ opncell_log_path | escape }}</code>
</div>
<script>
    $(function () {
        const grid = $("#grid-log");
        const toggle = $("#opncell_log_refresh_toggle");
        let timer = null;

        const bar = $("#grid-log-header .actionBar").addClass("opncell-log-toolbar");
        const top = $('<div class="opncell-log-top"></div>');
        const buttons = $('<div class="opncell-log-buttons"></div>');
        const details = $('<div class="opncell-log-details"></div>');
        top.append(bar.find(".search").first().detach());
        const severity = $("#severity_filter");
        top.append(severity.closest(".bootstrap-select").length ? severity.closest(".bootstrap-select").detach() : severity.detach());
        buttons.append($("#opncell_log_refresh").detach());
        buttons.append(bar.find(".actions").first().detach());
        buttons.append($("#command-wrapper").detach());
        top.append(buttons);
        details.append($("#opncell_log_path").detach());
        const timeframe = $("#validFrom_filter");
        if (timeframe.data("selectpicker")) { timeframe.selectpicker("refresh"); }
        details.append(timeframe.closest(".bootstrap-select").length ? timeframe.closest(".bootstrap-select").detach() : timeframe.detach());
        $("#filter_container").remove();
        bar.append(top, details);
        // Replace the core handlers: direct daemon files must not be unlinked.
        $("#flushlog").off("click").on("click", function (event) {
            event.preventDefault();
            BootstrapDialog.confirm({
                type: BootstrapDialog.TYPE_DANGER,
                title: "{{ lang._('Clear log') }}",
                message: "{{ lang._('Clear this log history? New records will continue to be written.') }}",
                callback: function (confirmed) {
                    if (!confirmed) { return; }
                    ajaxCall("/api/opncell/log/clear/{{scope}}", {}, function (result) {
                        if (result && result.status === "ok") {
                            grid.bootgrid("reload");
                        } else {
                            BootstrapDialog.alert(result && result.message ? result.message : "{{ lang._('Unable to clear the log file.') }}");
                        }
                    });
                }
            });
        });
        $("#exportbtn").off("click").on("click", function (event) {
            event.preventDefault();
            const params = new URLSearchParams();
            params.set("searchPhrase", $("input.search-field").val() || "");
            const options = $("#severity_filter option").map(function () { return this.value; }).get();
            const selected = $("#severity_filter").val();
            const exact = $("#exact_severity").hasClass("fa-toggle-on");
            const severity = exact ? [].concat(selected || []) : options.slice(0, options.indexOf(selected) + 1);
            params.set("severity", severity.join(","));
            const seconds = {hour: 3600, day: 86400, week: 604800, month: 2678400}[$("#validFrom_filter").val()];
            if (seconds) { params.set("validFrom", Math.floor(Date.now() / 1000) - seconds); }
            const link = document.createElement("a");
            link.href = "/api/opncell/log/query/{{scope}}/export?" + params.toString();
            document.body.appendChild(link);
            link.click();
            link.remove();
        });

        function refreshLatestPage() {
            if (!document.hidden && grid.attr("aria-busy") !== "true" && grid.bootgrid("getCurrentPage") === 1) {
                grid.bootgrid("reload");
            }
        }

        toggle.on("click", function () {
            if (timer === null) {
                timer = window.setInterval(refreshLatestPage, 5000);
                toggle.attr("aria-pressed", "true").addClass("active");
                refreshLatestPage();
            } else {
                window.clearInterval(timer);
                timer = null;
                toggle.attr("aria-pressed", "false").removeClass("active");
            }
        });
    });
</script>

<style>
#grid-log-header .opncell-log-toolbar {
    display: grid;
    grid-template-columns: minmax(180px, 380px) 200px max-content;
    gap: 12px 8px;
    align-items: center;
    text-align: left;
}
.opncell-log-top, .opncell-log-details { display: contents; }
#grid-log-header .opncell-log-top .search {
    grid-column: 1;
    grid-row: 1;
    float: none;
    width: 100%;
    min-width: 0;
    margin: 0;
}
.opncell-log-top > :nth-child(2) { grid-column: 2; grid-row: 1; }
.opncell-log-buttons {
    grid-column: 3;
    grid-row: 1;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
}
#grid-log-header .opncell-log-buttons .actions,
#grid-log-header .opncell-log-buttons #command-wrapper {
    float: none;
    display: inline-flex;
    flex-wrap: nowrap;
    width: auto;
    margin: 0;
}
#opncell_log_path {
    grid-column: 1;
    grid-row: 2;
    min-width: 0;
    margin: 0;
    padding: 0 !important;
}
.opncell-log-details > :nth-child(2) { grid-column: 2; grid-row: 2; }
@media (max-width: 1100px) {
    #grid-log-header .opncell-log-toolbar {
        grid-template-columns: minmax(180px, 380px) 200px;
    }
    .opncell-log-buttons { grid-column: 1 / -1; grid-row: 3; }
}
@media (max-width: 640px) {
    #grid-log-header .opncell-log-toolbar { grid-template-columns: minmax(0, 1fr); }
    .opncell-log-top > :nth-child(2) { grid-column: 1; grid-row: 2; }
    #opncell_log_path { grid-column: 1; grid-row: 3; }
    .opncell-log-details > :nth-child(2) { grid-column: 1; grid-row: 4; }
    .opncell-log-buttons { grid-column: 1; grid-row: 5; }
}
</style>
