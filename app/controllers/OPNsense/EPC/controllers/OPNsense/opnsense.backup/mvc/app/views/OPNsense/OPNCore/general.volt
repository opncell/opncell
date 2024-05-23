{#

This file is Copyright © 2023 by Digital Solutions
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

<script>
    var network = " ";
    const storedValue = localStorage.getItem("networkName");

    function UpdateOptions() {
        network = $('input:radio[name=network]:checked').val();
        localStorage.setItem("networkName", network);
        startServices(network);
        // ShowHideConfigFields();
    }

    function startServices(net) {

        $("#saveAct_networks").attr("style", "display:block");
        $("#saveAct_networks_progress").addClass("fa fa-spinner fa-pulse");
        ajaxCall(url = "/api/opncore/service/reconfigureAct/" + network, sendData = {}, callback = function (data, status) {
            updateServiceControlUI('opncore');
            $("#saveAct_networks_progress").removeClass("fa fa-spinner fa-pulse");
            $("#saveAct_networks").attr("style", "display:none");
            // ShowHideConfigFields();
            $("#saveAct_configs").attr("style", "display:block");
        });

    }

    function saveConfigurations() {
console.log("saving")
        saveFormToEndpoint(url = "/api/opncore/service/set", formid = 'frm_general_settings', callback_ok = function () {
            $("#saveAct_configs_progress").addClass("fa fa-spinner fa-pulse");
            ajaxCall(url = "/api/opncore/service/reconfigureAct/" + storedValue, sendData = {}, callback = function (data, status) {
                updateServiceControlUI('opncore');
                $("#restartServices").attr("style", "display:block");
                $("#saveAct_configs_progress").removeClass("fa fa-spinner fa-pulse");

            });
        }, true);

    }


    $(document).ready(function () {
        let data_get_map = {'frm_general_settings': "/api/opncore/general/get"};
        mapDataToFormUI(data_get_map).done(function (data) {
            console.log(data_get_map)
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
            ShowHideConfigFields();
            updateUI();
            updateServiceControlUI('opncore');
        });
        function ShowHideConfigFields() {
            console.log(network)
            if (network === "") {
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
            } else {
                $('tr[id="row_general.configs"]').removeClass('hidden');
                $('tr[id="row_general.plmnid_mcc"]').removeClass('hidden');
                $('tr[id="row_general.plmnid_mnc"]').removeClass('hidden');
                $('tr[id="row_general.tac"]').removeClass('hidden');
                $('tr[id="row_general.networkname"]').removeClass('hidden');
                $('tr[id="row_general.sst"]').removeClass('hidden');
                $('tr[id="row_general.dns"]').removeClass('hidden');
                $('tr[id="row_general.ca"]').removeClass('hidden');
                $("#saveAct_configs").attr("style", "display:block");
                $('tr[id="row_general.enablefour"]').addClass('hidden');
                $('tr[id="row_general.enablefiveSA"]').addClass('hidden');
                $('tr[id="row_general.enablefiveNSA"]').addClass('hidden');
                $('tr[id="row_general.enablemetrics"]').addClass('hidden');
                $('tr[id="row_general.metricsaddress"]').addClass('hidden');
                $('tr[id="row_general.metricsport"]').addClass('hidden');
            }
        }
        function updateUI() {
            if (network !== "") {
                const networks = $('input:radio[name=network]')
                for (const networkVal of networks) {
                    if (storedValue === networkVal.value) {
                        console.log(storedValue)
                        let labelId = networkVal.getAttribute("data-label");
                        let label = document.getElementById(labelId);
                        label.classList.add("active");
                        break; // No need to continue checking once we've found the match
                    }
                }
            }
        }

        $("#grid-other-configs").UIBootgrid({
            'search': '/api/opncore/general/startedServices',
            'get': 'api/opncore/general/getStartedServices',
            'set': 'api/opncore/general/setStartedServices',
        });

        // Automatically load the started services in the grid
        $('#configTab').on('click', function () {
            ajaxCall(url = "/api/opncore/general/startedServices", sendData = {}, callback = function (data, status) {

                $('#grid-other-configs').bootgrid('reload');

            });

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

<!-- Navigation bar -->
<ul class="nav nav-tabs" data-tabs="tabs" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#networks">{{ lang._('Network') }}</a></li>
    <li id="configTab"><a data-toggle="tab" href="#other-configs">{{ lang._('Configurations') }}</a></li>
</ul>
<div class="col-md-6 __mt">
    <div id="restartServices" class="alert alert-dismissible alert-info" style="display: none" role="alert">
        {{ lang._('Changes have been made, and services restarted.') }}
    </div>
</div>
<div class="tab-content content-box tab-content">
    <div id="networks" class="tab-pane fade in active">
        <div class="content-box" style="padding-bottom: 1.5em;">
            <div class="row __mt">
                <div class="col-12 __ml ">
                    <b class="__mb __ml">{{ lang._('Select a Network') }}:</b>
                    <form onChange="UpdateOptions()">
                        <div class="btn-group btn-group-s __ml __mb" data-toggle="buttons">
                            <label id="enablefour" class="btn btn-default">
                                <input type="radio" id="fourg" name="network" value="enablefour"
                                       data-label="enablefour"/>
                                {{ lang._('4G') }}
                            </label>&nbsp;&nbsp;&nbsp;
                            <label id="enablefiveSA" class="btn btn-default">
                                <input type="radio" id="fivegsa" name="network" value="enablefiveSA"
                                       data-label="enablefiveSA"/> {{ lang._('5G') }}
                            </label>
                            <label id="enablefiveNSA" class="btn btn-default">
                                <input type="radio" id="fivegnsa" name="network" value="enablefiveNSA"
                                       data-label="enablefiveNSA"/> {{ lang._('5G NSA') }}
                            </label>


                        </div>
                    </form>
                </div>
            </div>

            {{ partial("layout_partials/base_form",['fields':generalForm,'id':'frm_general_settings'])}}
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
        {{
        partial("layout_partials/base_dialog",['fields':formDialogConfigs,'id':'DialogOtherconfigs','label':lang._('Configurations:'),'hasSaveBtn':'true'])}}
        <table id="grid-other-configs" class="table table-condensed table-hover table-striped table-responsive"
               data-editDialog="DialogOtherconfigs">
            <thead>
            <tr>
                <th data-column-id="name" data-type="string" data-sortable="false" data-visible="true">{{
                    lang._('Service') }}
                </th>
                <th data-column-id="PID" data-type="string" data-sortable="false" data-visible="true">{{ lang._('PID')
                    }}
                </th>
                <th data-column-id="uuid" data-type="string" data-identifier="true" data-visible="false">{{
                    lang._('uuid') }}
                </th>
                <th data-column-id="tac" data-type="string" data-sortable="false" data-visible="false">{{ lang._('TAC')
                    }}
                </th>
                <th data-column-id="mnc" data-type="string" data-sortable="false" data-visible="false">{{ lang._('mnc')
                    }}
                </th>
                <th data-column-id="mcc" data-type="string" data-sortable="false" data-visible="false">{{ lang._('mcc')
                    }}
                </th>
                <th data-column-id="sst" data-type="string" data-sortable="false" data-visible="false">{{ lang._('sst')
                    }}
                </th>

                <!--                     <th data-column-id="metrics_addr" data-width="5em" data-type="string" data-sortable="false" data-visible="true">{{ lang._('metrics_addr') }}</th> -->
                <!--                     <th data-column-id="metrics_port" data-width="5em" data-type="string" data-sortable="false" data-visible="true">{{ lang._('metrics_port') }}</th> -->
                <th data-column-id="mme_add" data-type="string" data-sortable="false" data-visible="true">{{
                    lang._('MME:s1ap') }}
                </th>
                <th data-column-id="amf_add" data-type="string" data-sortable="false" data-visible="true">{{
                    lang._('AMF:ngap') }}
                </th>
                <th data-column-id="dns" data-type="string" data-sortable="false" data-visible="false">{{ lang._('DNS')
                    }}
                </th>

                <!--                 <th data-column-id="commands" data-formatter="commands" data-sortable="false">{{ lang._('Edit') }} </th>-->

            </tr>
            </thead>
            <tbody>

            </tbody>
        </table>
    </div>


</div>
<hr>
