<!-- Navigation bar -->
<ul class="nav nav-tabs" data-tabs="tabs" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#networks">{{ lang._('Network') }}</a></li>
    <li id="configTab"><a data-toggle="tab" href="#other-configs">{{ lang._('Configurations') }}</a></li>
    <li id="licenseTab"><a data-toggle="tab" href="#license">{{ lang._('License') }}</a></li>
</ul>

<div class="tab-content content-box tab-content">
    <!-- Network Tab-->
    <div id="networks" class="tab-pane fade in active">
        <div class="content-box" style="padding-bottom: 1.7em;">
            <div class="row __mt">
                <div class="col-md-12 __ml">
                    <b class="__mb">{{ lang._('Select a Network') }}:</b>

                    <form id="networkForm">
                        <div class="btn-group btn-group-s __mb" data-toggle="buttons">
                            <label id="enablefour" class="btn btn-default">
                                <input type="radio" name="network" value="enablefour" data-label="enablefour"/>
                                {{ lang._('4G') }}
                            </label>
                            <label id="enablefiveSA" class="btn btn-default">
                                <input type="radio" name="network" value="enablefiveSA" data-label="enablefiveSA"/>
                                {{ lang._('5G SA') }}
                            </label>
                            <label id="enablefiveNSA" class="btn btn-default">
                                <input type="radio" name="network" value="enablefiveNSA" data-label="enablefiveNSA"/>
                                {{ lang._('5G NSA') }}
                            </label>
                            <label id="enableupf" class="btn btn-default">
                                <input type="radio" name="network" value="enableupf" data-label="enableupf"/>
                                {{ lang._('UPF') }}
                            </label>
                        </div>
                    </form>

                </div>
            </div>
            {{ partial("layout_partials/base_form", ['fields': generalForm, 'id': 'frm_general_settings']) }}

            <div class="col-md-12 __mt">
                <button class="btn btn-primary" id="saveAct_networks" type="button" style="display:none;">
                    <b>{{ lang._('Services') }}</b> <i id="saveAct_networks_progress"></i>
                </button>
                <button class="btn btn-primary" id="saveAct_configs" type="button">
                    <b>{{ lang._('Save') }}</b> <i id="saveAct_configs_progress"></i>
                </button>
            </div>
        </div>
    </div>

    <!-- configs Tab -->
    <div id="other-configs" class="tab-pane fade">
        <table id="grid-other-configs" class="table table-condensed table-hover table-striped table-responsive"
               data-editDialog="DialogServiceConfig">
            <thead>
            <tr>
                <th data-column-id="name" data-width="20em">{{ lang._('Service') }}</th>
                <th data-column-id="PID">{{ lang._('PID') }}</th>
                <th data-column-id="mme_add">{{ lang._('Bind') }}</th>
                <th data-column-id="commands" data-formatter="commands" data-width="10em">{{ lang._('Status') }}</th>
            </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <!--License Tab -->
    <div id="license" class="tab-pane fade">
        <section class="col-xs-11 __mt">
            <p>OPNcell is Copyright &copy; 2023-2026<br>All rights reserved.</p>
            <p>Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:</p>
            <ol>
                <li>Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.</li>
                <li>Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.</li>
            </ol>
            <p>THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED...</p>
            <p>OPNcell uses <a href="https://github.com/open5gs/open5gs" target="_blank">Open5gs&reg;</a></p>

        </section>
    </div>
</div>

<hr>

{{ partial("layout_partials/base_dialog", ['fields': formDialogEditServiceConfig, 'id': 'DialogServiceConfig', 'label': lang._('Change Server Config:'), 'hasSaveBtn': true])}}

<script>
    $(document).ready(function () {
        let currentNetwork = "";

        mapDataToFormUI({'frm_general_settings': "/api/opncell/general/get"}).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');

            currentNetwork = localStorage.getItem('networkName') || "";
            console.log(`The current network is: ${currentNetwork}`);
            initNetworkSelection();
            updateUI();
        });

        // Network selection logic
        function initNetworkSelection() {

            $('#networkForm label.btn').on('click', function () {
                const selectedNetwork = $(this).find('input[name="network"]').val();
                console.log(`The selected network is: ${selectedNetwork}`);
                confirmNetworkChange(selectedNetwork);
            });
        }
        function confirmNetworkChange(newNetwork) {
            const previousNetwork = localStorage.getItem('networkName') || currentNetwork;

            // Special case: 5G SA requires Hnet configuration first
            if (newNetwork === 'enablefiveSA' && previousNetwork !== 'enablefiveSA') {
                window.location.href = "/ui/opncell/hnet";
                return;
            }
            // Normal network change (not 5G SA or switching away from it)
            proceedWithNetworkChange(newNetwork, previousNetwork);
        }

        function proceedWithNetworkChange(newNetwork, previousNetwork) {
            const isSameNetwork = previousNetwork === newNetwork;
            console.log(isSameNetwork);

            const message = isSameNetwork
                ? 'Re-loading the same network! This will restart all services. Proceed?'
                : 'You are about to change networks! Proceed?';

            BootstrapDialog.confirm({
                title: 'Confirm Network Change',
                message: message,
                type: BootstrapDialog.TYPE_WARNING,
                btnOKLabel: 'Yes',
                btnCancelLabel: 'No',
                callback: function (result) {
                    if (result) {
                        localStorage.setItem('networkName', newNetwork);
                        saveConfigurations(newNetwork);
                    } else {
                        // Revert selection
                        selectNetworkRadio(previousNetwork);
                    }
                }
            });
        }

        function selectNetworkRadio(network) {
            $('input[name="network"]').closest('label').removeClass('active');
            $('input[name="network"][value="' + network + '"]').prop('checked', true)
                .closest('label').addClass('active');
        }

        function saveConfigurations(network = null) {
            const targetNetwork = network || localStorage.getItem('networkName') || currentNetwork;
            if (!targetNetwork) return;

            BootstrapDialog.show({
                type: BootstrapDialog.TYPE_INFO,
                title: "{{ lang._('Activating Network') }}",
                closable: true,
                onshow: function (dialogRef) {
                    dialogRef.getModalBody().html(`
                    <div style="padding: 15px;">
                        {{ lang._('Network set-up in progress, please wait ...') }}
                        <i class="fa fa-cog fa-spin"></i>
                    </div>
                `);

                    saveFormToEndpoint("/api/opncell/service/set/" + targetNetwork, 'frm_general_settings', function (data) {
                        $("#saveAct_configs_progress").addClass("fa fa-spinner fa-pulse");
                        console.log(data);

                        ajaxCall("/api/opncell/service/reconfigureAct/" + targetNetwork, {}, function (data, status) {
                            $("#saveAct_configs_progress").removeClass("fa fa-spinner fa-pulse");
                            console.log(data);
                            updateServiceControlUI('opncell');
                            $("#grid-other-configs").bootgrid('reload');
                            dialogRef.close();
                        });
                    });
                }
            });
        }


        function ShowHideConfigFields(network) {
            const allRows = [
                'general.configs', 'general.plmnid_mcc', 'general.plmnid_mnc', 'general.tac',
                'general.networkname', 'general.sst', 'general.ue', 'general.peer',
                'general.dns', 'general.ca', 'general.enablemetrics',
                'general.metricsaddress', 'general.metricsport','general.enablefour','general.enableupf','general.enablefiveNSA','general.enablefiveSA'
            ];

            // Hide all by default
            allRows.forEach(row => $(`tr[id="row_${row}"]`).addClass('hidden'));

            if (!network) return;

            // Show common fields
            const commonFields = ['general.configs', 'general.plmnid_mcc', 'general.plmnid_mnc', 'general.tac',
                'general.networkname', 'general.sst', 'general.ue', 'general.peer',
                'general.dns', 'general.ca'];
            commonFields.forEach(row => $(`tr[id="row_${row}"]`).removeClass('hidden'));

            // Network-specific visibility
            if (network === 'enableupf') {
                // Hide most fields for UPF only mode
                ['general.configs', 'general.plmnid_mcc', 'general.plmnid_mnc', 'general.tac',
                    'general.networkname', 'general.sst', 'general.dns', 'general.ca'].forEach(row => {
                    $(`tr[id="row_${row}"]`).addClass('hidden');
                });
            }

            $("#saveAct_configs").show();
        }


        function updateUI() {
            const storedNetwork = localStorage.getItem('networkName');
            if (storedNetwork) {
                selectNetworkRadio(storedNetwork);
                ShowHideConfigFields(storedNetwork);
            } else if (currentNetwork) {
                ShowHideConfigFields(currentNetwork);
            }
        }

        const noEditServices = ['sgwcd', 'pcrfd', 'mongod', 'hssd'];

        let gridOtherConfigs = $("#grid-other-configs").UIBootgrid({
            ajax: true,
            selection: true,
            multiSelect: true,
            rowCount: [10, 25, 50, 100, 500, 1000],
            toggle:false,
            footer:false,
            search: '/api/opncell/general/startedServices/' +  (localStorage.getItem('networkName') || currentNetwork || "undefined"),
            options: {
                formatters: {
                    "commands": function (column, row) {
                        const isRunning = row.status === "running";
                        const isStopped = row.status === "stopped" || row.PID === "Stopped";
                        const isDisabled = row.status === "disabled";
                        const canEdit = !noEditServices.includes(row.serviceName);
                        if (isRunning) {
                            if (canEdit) {
                                return "<button type=\"button\" title=\"{{ lang._('start service') }}\" class=\"btn btn-xs btn-default label label-opnsense label-opnsense-sm label-success command-start\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-play fa-fw\"></span></button> " +
                                    "<button type=\"button\" title=\"{{ lang._('Restart service') }}\" class=\"btn btn-xs btn-default command-restart\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-repeat fa-fw\"></span></button>" +
                                    "<button type=\"button\" title=\"{{ lang._('Stop service') }}\" class=\"btn btn-xs btn-default command-stop\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-stop fa-fw\"></span></button>" +
                                    "<button type=\"button\" title=\"{{ lang._('Log file') }}\" class=\"btn btn-xs btn-default command-logfile\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-eye fa-fw\"></span></button>" +
                                    "<button type=\"button\" title=\"{{ lang._('Edit Config') }}\" class=\"btn btn-xs btn-default command-editConfig\" data-row-pid=\"" + row.PID + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-pencil fa-fw\"></span></button>";
                            } else {
                                return "<button type=\"button\" title=\"{{ lang._('start service') }}\" class=\"btn btn-xs btn-default label label-opnsense label-opnsense-sm label-success command-start\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-play fa-fw\"></span></button> " +
                                    "<button type=\"button\" title=\"{{ lang._('Restart service') }}\" class=\"btn btn-xs btn-default command-restart\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-repeat fa-fw\"></span></button>" +
                                    "<button type=\"button\" title=\"{{ lang._('Stop service') }}\" class=\"btn btn-xs btn-default command-stop\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-stop fa-fw\"></span></button>" +
                                    "<button type=\"button\" title=\"{{ lang._('Log file') }}\" class=\"btn btn-xs btn-default command-logfile\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-eye fa-fw\"></span></button>";
                            }

                        } else if (isStopped || isDisabled ) {
                            if (canEdit) {
                                return "<button type=\"button\" title=\"{{ lang._('Running') }}\" class=\"btn btn-xs btn-default label label-opnsense label-opnsense-sm label-danger command-start\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-play fa-fw\"></span></button> " +
                                    "<button type=\"button\" title=\"{{ lang._('Stop') }}\" class=\"btn btn-xs btn-default command-stop\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-stop fa-fw\"></span></button>" +
                                    "<button type=\"button\" title=\"{{ lang._('Log file') }}\" class=\"btn btn-xs btn-default command-logfile\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-eye fa-fw\"></span></button>" +
                                    "<button type=\"button\" title=\"{{ lang._('Edit Config') }}\" class=\"btn btn-xs btn-default command-editConfig\" data-row-pid=\"" + row.PID + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-pencil fa-fw\"></span></button>";

                            } else {
                                return "<button type=\"button\" title=\"{{ lang._('Running') }}\" class=\"btn btn-xs btn-default label label-opnsense label-opnsense-sm label-danger command-start\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-play fa-fw\"></span></button> " +
                                    "<button type=\"button\" title=\"{{ lang._('Stop') }}\" class=\"btn btn-xs btn-default command-stop\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-stop fa-fw\"></span></button>" +
                                    "<button type=\"button\" title=\"{{ lang._('Log file') }}\" class=\"btn btn-xs btn-default command-logfile\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-eye fa-fw\"></span></button>";
                            }

                        } else if (row.status === "unknown") {
                            return "<button type=\"button\" title=\"{{ lang._('start service') }}\" class=\"btn btn-xs btn-default label label-opnsense label-opnsense-sm label-success command-start\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-play fa-fw\"></span></button> " +
                                "<button type=\"button\" title=\"{{ lang._('Restart service') }}\" class=\"btn btn-xs btn-default command-restart\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-repeat fa-fw\"></span></button>" +
                                "<button type=\"button\" title=\"{{ lang._('Stop service') }}\" class=\"btn btn-xs btn-default command-stop\" data-row-id=\"" + row.uuid + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-stop fa-fw\"></span></button>";
                            // "<button type=\"button\" title=\"{{ lang._('Edit Config') }}\" class=\"btn btn-xs btn-default command-editConfig\" data-row-pid=\"" + row.PID + "\" data-row-service=\"" + row.serviceName + "\"><span class=\"fa fa-pencil fa-fw\"></span></button>";

                        }
                    },
                },
            },
        })

        gridOtherConfigs.on("loaded.rs.jquery.bootgrid", function () {
            $(this).find(".command-editConfig").off('click');
            $(this).find(".command-enable-selected").remove()
            $(this).find(".command-disable-selected").remove()
            // Start
            $(this).find(".command-start").on('click', function () {
                serviceAction('start', $(this).data('row-service'));
            });

            // Restart
            $(this).find(".command-restart").off('click').on('click', function () {
                serviceAction('restart', $(this).data('row-service'));
            });

            // Stop
            $(this).find(".command-stop").off('click').on('click', function () {
                serviceAction('stop', $(this).data('row-service'));
            });

            // Log
            $(this).find(".command-logfile").off('click').on('click', function () {
                let serviceName = $(this).data("row-service");
                let strippedServiceName = serviceName.slice(0,-1)    //remove the trailing 'd' [mmed -> mme]
                window.location.href="/ui/diagnostics/log/opncell/"+strippedServiceName
            });

            // Edit Config
            $(this).find(".command-editConfig").off('click').on('click', function () {
                const service = $(this).data('row-service');
                const pid = $(this).data('row-pid');
                editServiceConfig(service, pid);
            });
        });

        function serviceAction(action, serviceName) {
            const title = action === 'start' ? 'Starting Service' :
                action === 'restart' ? 'Restarting Service' : 'Stopping Service';
            console.log(action)
            BootstrapDialog.show({
                type: BootstrapDialog.TYPE_INFO,
                title: `{{ lang._('${title}') }}`,
                onshow: function (dialog) {
                    dialog.getModalBody().html(`<div style="padding:15px;">${title} in progress... <i class="fa fa-cog fa-spin"></i></div>`);

                    ajaxCall(url = `/api/opncell/service/${action}/${serviceName}`, sendData = {}, callback = function (data, status) {
                        // console.log(status)
                        console.log(data)

                        if (data.response  !== 'OK') {
                            console.log(data.response);
                            dialog.getModalBody().html(`<div style="padding:15px;">Failed to ${action}... <i class="fa fa-exclamation-circle"></i></div>`);
                            
                            setTimeout(function () {
                                dialog.close();
                            }, 4000);
                        }

                        $("#grid-other-configs").bootgrid('reload');
                        updateServiceControlUI('opncell');
                        // setTimeout(serviceWait, 45000);
                    });

                }
            });
        }

        function editServiceConfig(service, pid) {
            $('#DialogServiceConfig').modal({backdrop: 'static', keyboard: false});

            $("#btn_DialogServiceConfig_save").off('click').on('click', function () {
                const address = $("#addr").val();
                const params_array = [service,pid,address];
                console.log(params_array);
                ajaxCall(url = "/api/opncell/general/editServerConfig/" + params_array , sendData = {}, callback = function (data, status) {
                   console.log(status);
                   console.log(data);
                    $('#DialogServiceConfig').modal('hide');
                    gridOtherConfigs.bootgrid('reload')
                });

            });
        }


        $('#configTab').on('click', () => gridOtherConfigs.bootgrid('reload'));

        if (window.location.hash) {
            $('a[href="' + window.location.hash + '"]').tab('show');
        }
        $('.nav-tabs a').on('shown.bs.tab', function (e) {
            history.pushState(null, null, e.target.hash);
        });
    });
</script>
