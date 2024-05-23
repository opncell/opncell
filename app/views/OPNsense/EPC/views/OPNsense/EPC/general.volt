{#

OPNsense® is Copyright © 2014 – 2017 by Deciso B.V.
This file is Copyright © 2017 by Fabian Franz
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
    <li><a data-toggle="tab" href="#global-configs">{{ lang._('Global Configurations') }}</a></li>
    <li><a data-toggle="tab" href="#other-configs">{{ lang._('Other Configurations') }}</a></li>
    <li><a data-toggle="tab" href="#general">{{ lang._('General') }}</a></li>

</ul>
<div class="tab-content content-box tab-content">
  <div id="general" class="tab-pane fade in">
   <div class="content-box" style="padding-bottom: 1.5em;">
    {{ partial("layout_partials/base_form",['fields':generalForm,'id':'frm_general_settings'])}}

    <div class="col-md-12 __mt">

        <button class="btn btn-primary" id="saveAct" type="button"><b>{{ lang._('Save') }}</b> <i id="saveAct_progress"></i></button>
    </div>
</div>
</div>

<div id="networks" class="tab-pane fade in active">
    <div class="content-box" style="padding-bottom: 1.5em;">
        {{ partial("layout_partials/base_form",['fields':opncoreForm,'id':'frm_opncore_settings'])}}
        <div class="col-md-12 __mt">
            <button class="btn btn-primary" id="saveAct_networks" type="button"><b>{{ lang._('Save') }}</b> <i id="saveAct_networks_progress"></i></button>
        </div>
    </div>
</div>


 <div id="global-configs" class="tab-pane fade in">
        <div class="content-box" style="padding-bottom: 1.5em;">
            {{ partial("layout_partials/base_form",['fields':configForm,'id':'frm_config_settings'])}}
            <div class="col-md-12 __mt">
                <button class="btn btn-primary" id="saveAct_global_configs" type="button"><b>{{ lang._('Save') }}</b> <i id="saveAct_global_configs_progress"></i></button>
            </div>
        </div>
    </div>


<div id="other-configs" class="tab-pane fade in">

    <table id="grid-other-configs" class="table table-condensed table-hover table-striped table-responsive" data-editDialog="DialogOtherConfigs" >
        <thead>

  <tr>
                            <th data-column-id="name" data-type="string" data-sortable="false" data-visible="true">{{ lang._('Name') }}</th>

                            <th data-column-id="PID" data-type="string" data-sortable="false" data-visible="true">{{ lang._('PID') }}</th>
                         <th data-column-id="commands" data-width="7em" data-formatter="commands" data-sortable="false">{{ lang._('Edit') }} </th>
                        </tr>
        </thead>
        <tbody>
        </tbody>
    </table>
</div>

{{ partial("layout_partials/base_dialog",['fields':formDialogOtherConfigs,'id':'DialogOtherConfigs','label':lang._('Other configurations'),'hasSaveBtn':'true'])}}

</div>


<!-- <div class="content-box" style="padding-bottom: 1.5em;"> -->
<!--     {{ partial("layout_partials/base_form",['fields':generalForm,'id':'frm_general_settings'])}} -->
<!--     <div class="col-md-12"> -->
<!--         <hr /> -->
<!--         <button class="btn btn-primary" id="saveAct" type="button"><b>{{ lang._('Save') }}</b> <i id="saveAct_progress"></i></button> -->
<!--     </div> -->
<!-- </div> -->

<script>
    $( document ).ready(function() {
        var data_get_map = {'frm_general_settings':"/api/epc/general/get"};
        mapDataToFormUI(data_get_map).done(function(data){
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
        });
        updateServiceControlUI('epc');

        // link save button to API set action
        $("#saveAct").click(function(){
            saveFormToEndpoint(url="/api/epc/general/set", formid='frm_general_settings',callback_ok=function(){
                $("#saveAct_networks_progress").addClass("fa fa-spinner fa-pulse");
                ajaxCall(url="/api/epc/service/reconfigure", sendData={}, callback=function(data,status) {
                    updateServiceControlUI('epc');
                    $("#saveAct_networks_progress").removeClass("fa fa-spinner fa-pulse");
                });
            }, true);
        });

    });
</script>
