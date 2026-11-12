<div id="hnetTransferModal" class="modal fade" tabindex="-1" role="dialog" aria-labelledby="hnet_transfer_title">
    <div class="modal-dialog modal-lg" role="document"><div class="modal-content">
        <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="{{ lang._('Close') }}"><span aria-hidden="true">&times;</span></button>
            <h4 class="modal-title" id="hnet_transfer_title"></h4>
        </div>
        <div class="modal-body">
            <p>{{ lang._('Bundles contain private keys and are encrypted with your passphrase. Keep the bundle and passphrase safe; share them separately with the destination core administrator.') }}</p>
            <div class="form-group hnet-import-only">
                <label for="hnet_bundle_file">{{ lang._('Encrypted Hnet bundle') }}</label>
                <input id="hnet_bundle_file" type="file" accept=".json,.hnet" class="form-control">
            </div>
            <div class="form-group">
                <label for="hnet_bundle_passphrase">{{ lang._('Bundle passphrase') }}</label>
                <input id="hnet_bundle_passphrase" type="password" autocomplete="new-password" maxlength="1024" class="form-control">
                <span class="help-block">{{ lang._('At least 12 characters. The passphrase is not saved on the core.') }}</span>
            </div>
            <div class="form-group hnet-export-only">
                <label for="hnet_bundle_confirm">{{ lang._('Confirm passphrase') }}</label>
                <input id="hnet_bundle_confirm" type="password" autocomplete="new-password" maxlength="1024" class="form-control">
            </div>
            <div id="hnet_import_preview" hidden>
                <h5>{{ lang._('Import preview') }}</h5>
                <table class="table table-condensed table-striped"><thead><tr>
                    <th>{{ lang._('ID') }}</th><th>{{ lang._('Scheme') }}</th><th>{{ lang._('Action') }}</th><th>{{ lang._('Public key fingerprint') }}</th>
                </tr></thead><tbody id="hnet_import_preview_rows"></tbody></table>
                <p id="hnet_retained_keys"></p>
                <div class="checkbox" id="hnet_replace_choice"><label>
                    <input id="hnet_replace_conflicts" type="checkbox"> {{ lang._('Replace conflicting key IDs with the keys in this bundle') }}
                </label></div>
                <p>{{ lang._('Other existing keys are retained. A running UDM will restart briefly to load changes. Existing eSIMs must use the imported public key and key ID.') }}</p>
            </div>
            <div id="hnet_transfer_message" role="status" class="alert" hidden></div>
        </div>
        <div class="modal-footer">
            <button id="hnet_bundle_preview" type="button" class="btn btn-default hnet-import-only">{{ lang._('Preview import') }}</button>
            <button id="hnet_bundle_apply" type="button" class="btn btn-primary" disabled>{{ lang._('Import keys') }}</button>
            <button id="hnet_bundle_download" type="button" class="btn btn-primary hnet-export-only">{{ lang._('Download encrypted bundle') }}</button>
            <button type="button" class="btn btn-default" data-dismiss="modal">{{ lang._('Close') }}</button>
        </div>
    </div></div>
</div>
<script>
$(function () {
    const modal = $('#hnetTransferModal');
    const password = $('#hnet_bundle_passphrase');
    const file = $('#hnet_bundle_file');
    const apply = $('#hnet_bundle_apply');
    const message = $('#hnet_transfer_message');
    let bundle = null;
    let preview = null;
    let busy = false;

    function notice(text, failed) {
        message.text(text).removeClass('alert-danger alert-success').addClass(failed ? 'alert-danger' : 'alert-success').prop('hidden', false);
    }
    async function request(details) {
        const data = await ajaxCall('/api/opncell/hnet/manage', {payload: JSON.stringify(details)}, null);
        if (!data || data.result !== 'ok') {
            throw new Error(data && data.message ? data.message : "{{ lang._('Hnet operation failed. Please retry or check the service.') }}");
        }
        return data;
    }
    function errorText(error) {
        return error instanceof Error ? error.message : "{{ lang._('Unable to contact the Hnet service.') }}";
    }
    function invalidate() {
        bundle = null;
        preview = null;
        apply.prop('disabled', true);
        $('#hnet_import_preview').prop('hidden', true);
        $('#hnet_replace_conflicts').prop('checked', false);
    }
    function reset() {
        invalidate();
        password.val('');
        $('#hnet_bundle_confirm').val('');
        file.val('');
        $('#hnet_import_preview_rows').empty();
        message.text('').prop('hidden', true);
    }
    function open(importing) {
        reset();
        $('.hnet-import-only').toggle(importing);
        $('.hnet-export-only').toggle(!importing);
        apply.toggle(importing);
        $('#hnet_transfer_title').text(importing ? "{{ lang._('Import Hnet keys') }}" : "{{ lang._('Export Hnet keys') }}");
        modal.modal('show');
    }
    function setBusy(value) {
        busy = value;
        modal.find('button, input').prop('disabled', value);
        apply.prop('disabled', value || !preview || (preview.entries.some(e => e.action === 'replace') && !$('#hnet_replace_conflicts').prop('checked')));
    }
    $('#hnet_export_bundle').on('click', function () { open(false); });
    $('#hnet_import_bundle').on('click', function () { open(true); });
    password.on('input', invalidate);
    file.on('change', invalidate);
    $('#hnet_replace_conflicts').on('change', function () { setBusy(false); });
    modal.on('hide.bs.modal', function (event) { if (busy) { event.preventDefault(); } });
    modal.on('hidden.bs.modal', reset);

    $('#hnet_bundle_download').on('click', async function () {
        if (password.val() !== $('#hnet_bundle_confirm').val()) {
            notice("{{ lang._('Passphrases do not match.') }}", true); return;
        }
        setBusy(true);
        try {
            const data = await request({operation: 'export', passphrase: password.val()});
            const link = document.createElement('a');
            const url = URL.createObjectURL(new Blob([JSON.stringify(data.bundle, null, 2)], {type: 'application/json'}));
            link.href = url;
            link.download = 'opncell-hnet-keys.hnet.json';
            document.body.appendChild(link); link.click(); link.remove();
            setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
            password.val(''); $('#hnet_bundle_confirm').val('');
            notice("{{ lang._('Encrypted bundle downloaded. Keep its passphrase separately.') }}", false);
        } catch (error) { notice(errorText(error), true); }
        finally { setBusy(false); }
    });
    $('#hnet_bundle_preview').on('click', async function () {
        invalidate(); setBusy(true);
        try {
            const selected = file[0].files[0];
            if (!selected || selected.size > 1048576) { throw new Error("{{ lang._('Choose an Hnet bundle no larger than 1 MiB.') }}"); }
            bundle = JSON.parse(await selected.text());
            preview = await request({operation: 'plan', bundle: bundle, passphrase: password.val()});
            const body = $('#hnet_import_preview_rows').empty();
            const actions = {add: "{{ lang._('Add') }}", replace: "{{ lang._('Replace') }}", unchanged: "{{ lang._('Unchanged') }}"};
            preview.entries.forEach(function (entry) {
                const row = $('<tr></tr>');
                [entry.id, entry.scheme === 1 ? 'Profile A' : 'Profile B', actions[entry.action], entry.fingerprint].forEach(function (value) {
                    row.append($('<td style="overflow-wrap:anywhere"></td>').text(value));
                });
                body.append(row);
            });
            $('#hnet_retained_keys').text(preview.retained_ids.length ? "{{ lang._('Other key IDs retained:') }} " + preview.retained_ids.join(', ') : "{{ lang._('No other existing key IDs.') }}");
            $('#hnet_replace_choice').toggle(preview.entries.some(e => e.action === 'replace'));
            $('#hnet_import_preview').prop('hidden', false);
            message.prop('hidden', true);
        } catch (error) { invalidate(); notice(errorText(error), true); }
        finally { setBusy(false); }
    });
    apply.on('click', async function () {
        if (!preview) { return; }
        setBusy(true);
        try {
            const result = await request({operation: 'import', bundle: bundle, passphrase: password.val(), state: preview.state,
                                         replace_conflicts: $('#hnet_replace_conflicts').prop('checked')});
            reset();
            notice(result.message || "{{ lang._('Hnet keys imported.') }}", false);
        } catch (error) { invalidate(); notice(errorText(error), true); }
        finally { setBusy(false); }
    });
    $('#hnet_list_body').on('click', '.hnet-delete', function () {
        const button = $(this);
        BootstrapDialog.confirm({
            type: BootstrapDialog.TYPE_DANGER,
            title: "{{ lang._('Delete Hnet key') }}",
            message: "{{ lang._('Remove Hnet key ID') }} " + button.data('hnet-id') + "? {{ lang._('This removes its UDM reference, private key and public exports. eSIMs using this key may no longer register. A running UDM will restart briefly. A recovery backup is retained.') }}",
            callback: async function (confirmed) {
                if (!confirmed) { return; }
                button.prop('disabled', true);
                try {
                    await request({operation: 'delete', id: Number(button.data('hnet-id')), fingerprint: button.data('hnet-fingerprint')});
                    $('#existing_keys').trigger('click');
                } catch (error) { BootstrapDialog.alert(errorText(error)); }
                finally { button.prop('disabled', false); }
            }
        });
    });
});
</script>
