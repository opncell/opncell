<div class="content-box" style="padding: 15px;">
    <div class="clearfix" style="margin-bottom: 12px;">
        <button id="refresh-active-logs" class="btn btn-default pull-right" type="button">
            <span class="fa fa-refresh" aria-hidden="true"></span> {{ lang._('Refresh') }}
        </button>
        <h3 style="margin-top: 6px;">{{ lang._('Active daemon logs') }}</h3>
    </div>
    <p>{{ lang._('Diagnostic logs are available for currently running cellular daemons.') }}</p>
    <div id="active-logs-error" class="alert alert-danger" role="alert" style="display: none;"></div>
    <table class="table table-condensed table-striped">
        <thead><tr><th>{{ lang._('Daemon') }}</th><th>{{ lang._('PID') }}</th><th>{{ lang._('Log') }}</th></tr></thead>
        <tbody id="active-logs-rows"></tbody>
    </table>
</div>
<script>
$(function () {
    let busy = false;
    function refresh() {
        if (busy || document.hidden) { return; }
        busy = true;
        $.ajax({url: '/api/opncell/log/active', dataType: 'json'}).done(function (result) {
            if (!result || result.status !== 'ok' || !Array.isArray(result.rows)) {
                $('#active-logs-error').text("{{ lang._('Unable to inspect active daemons.') }}").show();
                return;
            }
            $('#active-logs-error').hide();
            const body = $('#active-logs-rows').empty();
            result.rows.forEach(function (row) {
                const tr = $('<tr></tr>');
                tr.append($('<td></td>').text(row.name));
                tr.append($('<td></td>').text(row.pids.join(', ')));
                const link = $('<a class="btn btn-default btn-xs"></a>')
                    .attr('href', '/ui/opncell/log/index/' + encodeURIComponent(row.name))
                    .text("{{ lang._('View log') }}");
                tr.append($('<td></td>').append(link));
                body.append(tr);
            });
            if (result.rows.length === 0) {
                body.append($('<tr></tr>').append($('<td colspan="3"></td>').text("{{ lang._('No cellular daemons are currently running.') }}")));
            }
        }).fail(function () {
            $('#active-logs-error').text("{{ lang._('Unable to inspect active daemons.') }}").show();
        }).always(function () { busy = false; });
    }
    $('#refresh-active-logs').on('click', refresh);
    $(document).on('visibilitychange', refresh);
    window.setInterval(refresh, 10000);
    refresh();
});
</script>
