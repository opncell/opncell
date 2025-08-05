{#

This file is Copyright © 2025 by Digital Solutions
Copyright (C) 2024 - 2025 Primrose Namirimu primrose@ds.co.ug>
Copyright (C) 2024 - 2025 Wireless Laboratories <rob.hamblet@wire-labs.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1.  Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2.  Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

#}



<!-- Navigation bar -->
<ul class="nav nav-tabs" data-tabs="tabs" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#networks">{{ lang._('Network') }}</a></li>
    <li id="configTab"><a data-toggle="tab" href="#other-configs">{{ lang._('Configurations') }}</a></li>
    <li id="licenseTab"><a data-toggle="tab" href="#license">{{ lang._('License') }}</a></li>
</ul>

<div class="tab-content content-box tab-content">
    <div id="networks" class="tab-pane fade in active">
        <div class="content-box" style="padding-bottom: 1.7em;">
            <div class="row __mt">
                <div class="col-md-12 __ml ">
                    <b class="__mb">{{ lang._('Select a Network ') }}:</b>
                    <form onChange="confirmNetworkChange()">
                        <div class="btn-group btn-group-s __mb" data-toggle="buttons">
                            <label id="enablefour" class="btn btn-default">
                                <input type="radio" id="fourg" name="network" value="enablefour"
                                       data-label="enablefour"/>
                                {{ lang._('4G') }}
                            </label>&nbsp;&nbsp;

                            <label id="enablefiveSA" class="btn btn-default">
                                <input type="radio" id="fivegsa" name="network" value="enablefiveSA"
                                       data-label="enablefiveSA"/> {{ lang._('5G')
                                }}
                            </label>
                            <label id="enablefiveNSA" class="btn btn-default">
                                <input type="radio" id="fivegnsa" name="network" value="enablefiveNSA"
                                       data-label="enablefiveNSA"/> {{
                                lang._('5G NSA') }}
                            </label>
                            <label id="enableupf" class="btn btn-default">
                                <input type="radio" id="upf" name="network" value="enableupf"
                                       data-label="enableupf"/>
                                {{ lang._('UPF') }}
                            </label>&nbsp;&nbsp;
                        </div>
                    </form>
                    {{ partial("layout_partials/base_form",['fields':generalForm,'id':'frm_general_settings'])}}
                </div>
            </div>

            <div class="col-md-12 __mt">
                <button class="btn btn-primary" style="display: none" id="saveAct_networks" type="button"><b>{{
                    lang._('Services') }}</b> <i id="saveAct_networks_progress"></i></button>
            </div>
            <div class="col-md-12 __mt">
                <button class="btn btn-primary" style="display: none" id="saveAct_configs" type="button"
                        onClick="saveConfigurations()"><b>{{ lang._('Save') }}</b> <i id="saveAct_configs_progress"></i>
                </button>
            </div>
        </div>
    </div>

    <div id="other-configs" class="tab-pane fade in">

        <table id="grid-other-configs" class="table table-condensed table-hover table-striped table-responsive"
               data-editDialog="DialogServiceConfig">
            <thead>
            <tr>

                <th data-column-id="name" data-type="string" data-width="20em" data-sortable="false" data-visible="true">{{ lang._('Service') }}</th>
                <th data-column-id="PID" data-type="string" data-sortable="false" data-visible="true">{{ lang._('PID') }}</th>
                <th data-column-id="mme_add" data-type="string" data-sortable="false" data-visible="true">{{ lang._('bind') }}</th>
                <th data-column-id="commands" data-formatter="commands" data-width="10em" data-sortable="false">{{ lang._('Status') }} </th>

            </tr>
            </thead>
            <tbody>

            </tbody>
        </table>
    </div>

    <div id="license" class="tab-pane fade in">
        <section class="col-xs-11 __mt">
            <p>OPNcell is Copyright &copy; 2023-2025<br>All rights reserved.</p>
            <p>Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:</p>
            <ol><li>Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.</li>
                <li>Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.</li></ol>
            <p>THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
                INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
                AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
                THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
                EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
                PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
                OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
                WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
                OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
                ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.</p>

            <p>OPNcell uses <a href="https://github.com/open5gs/open5gs" target="_blank">Open5gs&reg;</a> <small>(Copyright &copy; 2019-2025 by Sukchan Lee, acetcom@gmail.com. All rights reserved.)</small></p>
            <p>OPNcell includes various freely available software packages and ports.
                The incorporated third party tools are listed <a href="/ui/core/firmware#packages">here</a>.</p>
            <p>The authors of OPNcell would like to thank all contributors for their efforts.</p>
        </section>
        <br/>
    </div>


</div>
<hr>
<script>
    var network = " ";
    function getVar() {
        return localStorage.getItem('networkName');
    }

    function confirmNetworkChange(){
        let lastNetwork = getVar()
        let checkedNetwork = $('input:radio[name=network]:checked').val();
        localStorage.setItem("networkName", checkedNetwork);
        let message;
        if (lastNetwork === checkedNetwork) {
            message = 'Re-loading the same network!. This will restart all its services. Proceed with Action?'
        } else {
            message = "You are about to change networks! Proceed with action?"
        }
        BootstrapDialog.confirm({
            title: 'Confirm Network Change',
            message: message,
            type: BootstrapDialog.TYPE_WARNING,
            btnOKLabel: 'Yes',
            btnCancelLabel: 'No',
            callback: function(result) {
                if (result) {
                    saveConfigurations();
                } else {
                    // User cancelled, revert selection
                    $('input[name="network"][value="' + checkedNetwork + '"]').prop('checked', true);
                }
            }
        });
    }

    function saveConfigurations() {
        let checkedNetwork = getVar()
        console.log(checkedNetwork)
        BootstrapDialog.show({
            type:BootstrapDialog.TYPE_INFO,
            title: "{{ lang._('Activating Network') }}",
            closable: true,
            onshow: function(dialogRef){

                dialogRef.getModalBody().html(
                    '<div style="padding: 15px;">' +
                    "{{ lang._('Network set-up in progress, please wait ...') }}" +
                    ' <i class="fa fa-cog fa-spin"></i>' +
                    '</div>'

                );

                saveFormToEndpoint(url="/api/opncell/service/set/" + checkedNetwork, formid='frm_general_settings', callback_ok = function () {

                    $("#saveAct_configs_progress").addClass("fa fa-spinner fa-pulse");
                    ajaxCall(url = "/api/opncell/service/reconfigureAct/" + checkedNetwork,
                        sendData = {},
                        callback = function (data, status) {
                            updateServiceControlUI('opncell');

                            $("#saveAct_configs_progress").removeClass("fa fa-spinner fa-pulse");
                            dialogRef.close()

                        });

                }, true);

            },
        });

    }

    function ShowHideConfigFields() {
        if (network === "") {
            $('tr[id="row_general.configs"]').addClass('hidden');
            $('tr[id="row_general.plmnid_mcc"]').addClass('hidden');
            $('tr[id="row_general.plmnid_mnc"]').addClass('hidden');
            $('tr[id="row_general.tac"]').addClass('hidden');
            $('tr[id="row_general.networkname"]').addClass('hidden');
            $('tr[id="row_general.sst"]').addClass('hidden');
            $('tr[id="row_general.ue"]').addClass('hidden');
            $('tr[id="row_general.peer"]').addClass('hidden');
            $('tr[id="row_general.dns"]').addClass('hidden');
            $('tr[id="row_general.ca"]').addClass('hidden');
            $('tr[id="row_general.enablefour"]').addClass('hidden');
            $('tr[id="row_general.enableupf"]').addClass('hidden');
            $('tr[id="row_general.enablefiveSA"]').addClass('hidden');
            $('tr[id="row_general.enablefiveNSA"]').addClass('hidden');
            $('tr[id="row_general.enablemetrics"]').addClass('hidden');
            $('tr[id="row_general.metricsaddress"]').addClass('hidden');
            $('tr[id="row_general.metricsport"]').addClass('hidden');
        } else {
            $('tr[id="row_general.configs"]').removeClass('hidden');
            $('tr[id="row_general.plmnid_mcc"]').removeClass('hidden');
            $('tr[id="row_general.plmnid_mnc"]').removeClass('hidden');
            $('tr[id="row_general.tac"]').removeClass('hidden');
            $('tr[id="row_general.networkname"]').removeClass('hidden');
            $('tr[id="row_general.sst"]').removeClass('hidden');
            $('tr[id="row_general.ue"]').removeClass('hidden');
            $('tr[id="row_general.peer"]').removeClass('hidden');
            $('tr[id="row_general.dns"]').removeClass('hidden');
            $('tr[id="row_general.ca"]').removeClass('hidden');
            $("#saveAct_configs").attr("style", "display:block");
            $('tr[id="row_general.enablefour"]').addClass('hidden');
            $('tr[id="row_general.enableupf"]').addClass('hidden');
            $('tr[id="row_general.enablefiveSA"]').addClass('hidden');
            $('tr[id="row_general.enablefiveNSA"]').addClass('hidden');
            $('tr[id="row_general.enablemetrics"]').addClass('hidden');
            $('tr[id="row_general.metricsaddress"]').addClass('hidden');
            $('tr[id="row_general.metricsport"]').addClass('hidden');
        }

        if (network ==='enableupf'){
            $('tr[id="row_general.configs"]').addClass('hidden');
            $('tr[id="row_general.plmnid_mcc"]').addClass('hidden');
            $('tr[id="row_general.plmnid_mnc"]').addClass('hidden');
            $('tr[id="row_general.tac"]').addClass('hidden');
            $('tr[id="row_general.networkname"]').addClass('hidden');
            $('tr[id="row_general.sst"]').addClass('hidden');
            $('tr[id="row_general.dns"]').addClass('hidden');
            $('tr[id="row_general.ca"]').addClass('hidden');
            $('tr[id="row_general.enablefour"]').addClass('hidden');
            $('tr[id="row_general.enablefiveSA"]').addClass('hidden');
            $('tr[id="row_general.enablefiveNSA"]').addClass('hidden');
            $('tr[id="row_general.enablemetrics"]').addClass('hidden');
            $('tr[id="row_general.metricsaddress"]').addClass('hidden');
            $('tr[id="row_general.metricsport"]').addClass('hidden');
        }
    }

    $(document).ready(function () {
        let data_get_map = {'frm_general_settings': "/api/opncell/general/get"};

        mapDataToFormUI(data_get_map).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
            ShowHideConfigFields();
            updateUI();
            updateServiceControlUI('opncell');
        });

        function active(val){
            const networks = $('input:radio[name=network]')
            console.log(networks)
            for (const networkVal of networks) {
                if (val === networkVal.value) {
                    ShowHideConfigFields()
                    var labelId = networkVal.getAttribute("data-label");
                    var label = document.getElementById(labelId);
                    label.classList.add("active");
                    break; // No need to continue checking once we've found the match

                }
            }
        }

        function updateUI() {

            if (network && network !== "") {
                const storedValue = getVar();
                if (storedValue != null){
                    active(storedValue)

                }
                else {
                    ajaxCall(url = '/api/opncell/general/get' , sendData = {}, callback = function (data) {
                        console.log(data.general)
                        const getNodes = data.general

                        const result = Object.keys(getNodes)
                            .filter(key => key.startsWith("enable")) // Filter keys starting with "enable"
                            .find(key => getNodes[key] === "1"); // Find the key with value 1 ergo, checked network
                        active(result)
                        console.log(result);

                    });
                }

            }

        }

        let noEdit = ['sgwcd','pcrfd','mongod','hssd'];

        let gridOtherConfigs = $("#grid-other-configs").UIBootgrid({
            ajax: true,
            selection: true,
            multiSelect: true,
            rowCount: [10, 25, 50, 100, 500, 1000],
            search: '/api/opncell/general/startedServices/' + getVar(),
            options: {
                formatters: {
                    "commands": function (column, row) {
                        if (row.status === "running") {
                            if (!(noEdit.includes(row.serviceName))) {
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

                        } else if (row.status === "stopped" || row.status === "disabled" || row.PID === "Stopped") {
                            if (!(noEdit.includes(row.serviceName))) {
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

                }
            }
        });
        function serviceWait() {
            $.ajax({
                url: '/ui/opncell/general#other-configs',
                timeout: 2500
            }).fail(function () {
                setTimeout(serviceWait, 2500);
            }).done(function () {
                $(location).attr('href', '/ui/opncell/general#other-configs');
            });
        }

        gridOtherConfigs.on("loaded.rs.jquery.bootgrid", function (e) {
            //start service
            gridOtherConfigs.find(".command-start").on("click", function (e) {
                var serviceName = $(this).data("row-service");
                console.log(serviceName)
                BootstrapDialog.show({
                    type:BootstrapDialog.TYPE_INFO,
                    title: "{{ lang._('Starting Service') }}",
                    closable: true,
                    onshow: function(dialogRef){
                        dialogRef.getModalBody().html(
                            '<div style="padding: 15px;">' +
                            "{{ lang._(' The service is starting, please wait ...') }}" +
                            ' <i class="fa fa-cog fa-spin"></i>' +
                            '</div>'
                        );


                        ajaxCall(url = '/api/opncell/service/start/' + serviceName, sendData = {}, callback = function (data, status) {
                            console.log(status)
                            console.log(data)

                            dialogRef.close()

                        });
                        $("#grid-other-configs").bootgrid('reload');
                        updateServiceControlUI('opncell');
                        setTimeout(serviceWait, 45000);
                    },
                });

            });

            // restart service
            gridOtherConfigs.find(".command-restart").on("click", function (e) {

                var serviceName = $(this).data("row-service");
                console.log(serviceName)

                BootstrapDialog.show({
                    type:BootstrapDialog.TYPE_INFO,
                    title: "{{ lang._('Restarting Service') }}",
                    closable: true,
                    onshow: function(dialogRef){
                        dialogRef.getModalBody().html(
                            '<div style="padding: 15px;">' +
                            "{{ lang._('The service is restarting , please wait ...') }}" +
                            ' <i class="fa fa-cog fa-spin"></i>' +
                            '</div>'
                        );
                        ajaxCall(url = '/api/opncell/service/restart/' + serviceName, sendData = {}, callback = function (data, status) {
                            console.log(status)
                            console.log(data)

                            dialogRef.close()

                        });
                        $("#grid-other-configs").bootgrid('reload');
                        updateServiceControlUI('opncell');
                        setTimeout(serviceWait, 45000);
                    },
                });
            });

            //  stop service
            gridOtherConfigs.find(".command-stop").on("click", function (e) {
                var serviceName = $(this).data("row-service");
                console.log(serviceName)
                BootstrapDialog.show({
                    type:BootstrapDialog.TYPE_INFO,
                    title: "{{ lang._(' Stopping Service') }}",
                    closable: true,
                    onshow: function(dialogRef){
                        dialogRef.getModalBody().html(
                            '<div style="padding:15px;">' +
                            "{{ lang._(' The service is stopping , please wait ...') }}" +
                            ' <i class="fa fa-cog fa-spin"></i>' +
                            '</div>'
                        );

                        ajaxCall(url = '/api/opncell/service/stop/' + serviceName, sendData = {}, callback = function (data, status) {

                            dialogRef.close()

                        });
                        $("#grid-other-configs").bootgrid('reload');
                        updateServiceControlUI('opncell');
                    },
                });

            });

            //  fetch log file
            gridOtherConfigs.find(".command-logfile").on("click", function (e) {
                var serviceName = $(this).data("row-service");
                console.log(serviceName)
                let strippedServiceName = serviceName.slice(0,-1)    //remove the trailing 'd' mmed -> mme
                console.log(strippedServiceName)
                window.location.href="/ui/diagnostics/log/opncell/"+strippedServiceName
            });


            // edit service config
            const editDlg = $(this).attr('data-editDialog');

            gridOtherConfigs.find(".command-editConfig").on("click", function (e) {
                // edit dialog id to use
                console.log(editDlg)
                const gridId = $(this).attr('id');

                if (editDlg !== undefined ) {
                    let pid = $(this).data("row-pid");
                    let server = $(this).data("row-service");
                    console.log(server,pid)
                    let y = [server]
                    y.push(pid)

                    $('#' + editDlg).modal({backdrop: 'static', keyboard: false});
                    let inputElement = document.getElementById("addr")
                    // define save action
                    $("#btn_" + editDlg + "_save").unbind('click').click(function () {
                        console.log("clicked")
                        let v = inputElement.value
                        y.push(v)
                        ajaxCall(url = "/api/opncell/general/editServerConfig/" + y , sendData = {}, callback = function (data, status) {
                            $("#" + editDlg).modal('hide');
                            std_bootgrid_reload(gridId);
                            $('#grid-other-configs').bootgrid('reload')
                        });

                    });
                } else {
                    console.log("[grid] action get or data-editDialog missing")
                }
            });

        });

        // Automatically load the started services in the grid
        $('#configTab').on('click', function () {
            var storedValue =  getVar()
            ajaxCall(url = "/api/opncell/general/startedServices/" + storedValue, sendData = {}, callback = function (data, status) {
                $('#grid-other-configs').bootgrid('reload')

            });

            updateServiceControlUI('opncell');
        });

        // update history on tab state and implement navigation
        if (window.location.hash !== "") {
            $('a[href="' + window.location.hash + '"]').click()
        }
        $('.nav-tabs a').on('shown.bs.tab', function (e) {
            history.pushState(null, null, e.target.hash);
        });

    });


</script>
{{ partial("layout_partials/base_dialog",['fields':formDialogEditServiceConfig,'id':'DialogServiceConfig','label':lang._('Change Server Config:'),'hasSaveBtn':'true'])}}