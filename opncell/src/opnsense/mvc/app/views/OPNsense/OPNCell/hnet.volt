
<div class="tab-content content-box tab-content">
    <!-- Network Tab -->
    <div id="networks" class="tab-pane fade in active">
        <div class="content-box" style="padding-bottom: 1.7em;">
            <div class="row __mt">
                <div class="col-md-12 __ml">
                    <b class="__mb">5G SA requires Home Network (Hnet) configuration in the UDM yml, for SUCI concealment.</b>
                    <p>Once the key-pair is generated, the private key is stored in <code>/usr/ports/open5gs/install/etc/open5gs/hnet/</code>.<br>
                        Use the public key when creating the SIM profile.<br>
                        These values will be ignored if the UE uses the null (0) protection scheme.</p>
                    <p> Both the HEX and PEM versions of the public key will be availed in the filepath you provide. </p>
                </div>
            </div>

            {{ partial("layout_partials/base_form", ['fields': hnetForm, 'id': 'frm_hnet_settings']) }}
            <div class="row __mt">
                <div class="col-md-12 __ml">
                    <button class="btn btn-primary mr-2" id="saveAct_hnet" type="button">
                        <b>{{ lang._('Save & Generate Keys') }}</b>
                        <i id="saveAct_hnet_progress"></i>
                    </button>
                    <button class="btn btn-primary __ml" id="existing_keys" type="button">
                        <b>{{ lang._('Use existing keys') }}</b>
                        <i id="activate_progress"></i>
                    </button>

                </div>


            </div>

        </div>
    </div>
</div>
<!-- HNET Key Generation Result Modal -->
<div id="hnetResultModal" class="modal fade" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">

            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="fa fa-key fa-fw"></i>
                    HNET Key Generation Result
                </h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>

            <div class="modal-body">
                <div class="content-box">
                    <!-- Private Key Path -->
                    <hr>
                    <div class="form-group">
                        &nbsp;&nbsp;<label>Hnet ID</label>
                        &nbsp;&nbsp;<div class="well well-sm" id="hnet_id"></div>
                    </div>

                    <div class="form-group">
                        &nbsp;&nbsp;<label>Private Key Path</label>
                        &nbsp;&nbsp;<div class="well well-sm" id="hnet_result_priv_path"></div>
                    </div>

                    <!-- Public Key Path -->
                    <div class="form-group">
                        &nbsp;&nbsp;<label>Public Key Path (PEM)</label>
                        &nbsp;&nbsp;<div class="well well-sm" id="hnet_result_path"></div>
                    </div>

                    <!-- Public Key HEX -->
                    <div class="form-group">
                       &nbsp;&nbsp; <label>Public Key (HEX)</label>
                        &nbsp;&nbsp;  <div class="well well-sm" style="word-break: break-all;" id="hnet_result_hex"></div>

                        &nbsp;&nbsp; <button class="btn btn-primary" id="copy_hex_btn">
                            <i class="fa fa-copy"></i> Copy HEX
                        </button>
                    </div>

                </div>



            </div>

            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-dismiss="modal">
                    Close
                </button>
            </div>

        </div>
    </div>
</div>

<script>
    $(document).ready(function () {
        let get_hnet_data = {'frm_hnet_settings': "/api/opncell/hnet/get"};
        mapDataToFormUI(get_hnet_data).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
        });
        updateServiceControlUI('opncell')

        function activateNetwork(network) {
            BootstrapDialog.show({
                type: BootstrapDialog.TYPE_INFO,
                title: "{{ lang._('Activating 5G SA') }}",
                closable: true,
                onshow: function (dialogRef) {
                    dialogRef.getModalBody().html(`
                <div style="padding: 15px;">
                    {{ lang._('Network set-up in progress, please wait ...') }}
                    <i class="fa fa-cog fa-spin"></i>
                </div>
            `);
                    ajaxCall("/api/opncell/service/reconfigureAct/" + network, {}, function () {
                        $("#saveAct_configs_progress").removeClass("fa fa-spinner fa-pulse");
                        updateServiceControlUI("opncell");
                        $("#grid-other-configs").bootgrid("reload");
                        dialogRef.close();
                        console.log(localStorage.getItem('networkName'));
                    });
                }
            });
        }
        $("#hnetResultModal").on("hidden.bs.modal", function () {
            const network = localStorage.getItem("networkName");

            if (network !== "enablefiveSA") {

                const message = 'Keys successfully generated! Do you want to activate 5G SA network?';
                let newNetwork = "enablefiveSA";

                BootstrapDialog.confirm({
                    title: 'Confirm Network Change',
                    message: message,
                    type: BootstrapDialog.TYPE_WARNING,
                    btnOKLabel: 'Proceed',
                    btnCancelLabel: 'No',
                    callback: function (result) {
                        if (result) {
                            localStorage.setItem('networkName', newNetwork);
                            activateNetwork(newNetwork);
                        } else {
                            // Revert selection
                            $('input[name="network"][value="' + network + '"]').prop('checked', true);
                        }
                    }
                });

            }
        });

        $("#saveAct_hnet").off('click').on('click', function () {

            $("#saveAct_hnet_progress").addClass("fa fa-spinner fa-pulse");
            $("#saveAct_hnet").prop("disabled", true);

            BootstrapDialog.confirm({
                title: 'Generate keys for SUCI concealment!',
                message: 'Proceed to generate keys for SUCI concealment?',
                type: BootstrapDialog.TYPE_WARNING,
                btnOKLabel: 'Proceed',
                btnCancelLabel: 'No',
                callback: function (result) {
                    if (result) {
                        saveFormToEndpoint('/api/opncell/hnet/add',
                            formid = 'frm_hnet_settings',
                            function (data, status) {
                                console.log(data);

                                $("#saveAct_hnet_progress").removeClass("fa fa-spinner fa-pulse");

                                console.log(data.data);
                                let payload = data.data;
                                if (typeof payload === "string") {
                                    payload = JSON.parse(payload);
                                }

                                // fill result modal
                                if (payload.result === "ok") {
                                    $("#hnetResultModal").modal("show");

                                    $("#hnet_result_path").text(payload.public_key_path);
                                    $("#hnet_result_priv_path").text(payload.private_key_path);
                                    $("#hnet_result_hex").text(payload.public_key_hex);
                                    $("#hnet_id").text(payload.id);

                                } else {
                                    let msg = payload.error;
                                    BootstrapDialog.show({
                                        message:"{{ lang._ ('Key generation failed with error  ') }}" + msg,
                                        type: BootstrapDialog.TYPE_ERR,
                                        title: "{{ lang._('Error! Something went wrong.') }}",
                                        closable: true,
                                        onshow: function (dialogRef) {

                                        }
                                    });
                                }
                                $("#saveAct_hnet_progress").removeClass("fa fa-spinner fa-pulse");
                                $("#saveAct_hnet").prop("disabled", false);

                            },
                            true
                        );
                    } else {
                        $("#saveAct_hnet_progress").removeClass("fa fa-spinner fa-pulse");
                        $("#saveAct_hnet").prop("disabled", false);
                    }
                }
            });

        });
        $("#existing_keys").off('click').on("click", function () {
            const network = localStorage.getItem("networkName");
            const dict = { enablefiveSA : "5G NSA" ,
                           enablefour : "4G",
                            enableupf : "UPF"
                        }
            console.log(network);
            let message;
            if (network !== "enablefiveSA") {
               message =  'The' + dict[network] + ' network is currently active! Do you want to switch to 5G SA?';

            } else {
                message = 'Re-loading the network! This will restart all services. Proceed?'
            }
            let newNetwork = "enablefiveSA";
                    BootstrapDialog.confirm({
                        title: 'Confirm Network Change',
                        message: message,
                        type: BootstrapDialog.TYPE_WARNING,
                        btnOKLabel: 'Proceed',
                        btnCancelLabel: 'No',
                        callback: function (result) {
                            if (result) {
                                localStorage.setItem('networkName', newNetwork);
                                activateNetwork(newNetwork);
                            } else {
                                // Revert selection
                                $('input[name="network"][value="' + dict[network] + '"]').prop('checked', true);
                            }
                        }
                    });


        });

        $("#copy_hex_btn").on("click", function () {
            const text = $("#hnet_result_hex").text();

            navigator.clipboard.writeText(text).then(() => {
                $(this).text("Copied!");
                setTimeout(() => $(this).text("Copy HEX"), 1500);
            });
        });

        $("#copy_path_btn").on("click", function () {
            const text = $("#hnet_result_path").text();

            navigator.clipboard.writeText(text).then(() => {
                $(this).text("Copied!");
                setTimeout(() => $(this).text("Copy Public Path"), 1500);
            });
        });
    });
</script>