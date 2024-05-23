    <div class="content-box" style="padding-bottom: 1.5em;">
        {{ partial("layout_partials/base_form",['fields':generalForm,'id':'frm_GeneralSettings'])}}
        <div class="col-md-12">
            <hr />
            <button class="btn btn-primary" id="saveAct" type="button"><b>{{ lang._('Save') }}</b> <i id="saveAct_progress"></i></button>
        </div>
    </div>

    <script>
        $( document ).ready(function() {
            var data_get_map = {'frm_general_settings':"/api/helloworld/settings/get"};
            mapDataToFormUI(data_get_map).done(function(data){
                formatTokenizersUI();
                $('.selectpicker').selectpicker('refresh');
            });
            updateServiceControlUI('helloworld');

            // link save button to API set action
            $("#saveAct").click(function(){
                saveFormToEndpoint(url="/api/helloworld/settings/set", formid='frm_general_settings',callback_ok=function(){
                    $("#saveAct_progress").addClass("fa fa-spinner fa-pulse");
                    ajaxCall(url="/api/helloworld/service/start", sendData={}, callback=function(data,status) {
                        updateServiceControlUI('helloworld');
                        $("#saveAct_progress").removeClass("fa fa-spinner fa-pulse");
                    });
                }, true);
            });
        });
    </script>



