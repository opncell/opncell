{{ partial("layout_partials/base_form",['fields':generalFiveGSAForm,'id':'general5GSAForm'])}}
    <script type="text/javascript">
        $( document ).ready(function() {
            var data_get_map = {'frm_GeneralSettings':"/api/helloworld/settings/get"};
            mapDataToFormUI(data_get_map).done(function(data){
                // place actions to run after load, for example update form styles.
            });

            // link save button to API set action
            $("#saveAct").click(function(){
                saveFormToEndpoint(url="/api/helloworld/settings/set",formid='frm_GeneralSettings',callback_ok=function(){
                    // action to run after successful save, for example reconfigure service.
                });
            });


        });
    </script>
<hr>
    <div class="col-md-12">
        <button class="btn btn-primary"  id="saveAct" type="button"><b>{{ lang._('Save') }}</b></button>
    </div>




<!-- <table id="grid-key-pairs" class="table table-condensed table-hover table-striped" data-editDialog="dialog5GSA" data-editAlert="KPChangeMessage"> -->
<!--         <thead> -->
<!--         <tr> -->
<!--             <th data-column-id="uuid" data-type="string" data-identifier="true" data-visible="false">{{ lang._('ID') }}</th> -->
<!--             <th data-column-id="name" data-type="string">{{ lang._('Name') }}</th> -->
<!--             <th data-column-id="keyType" data-width="20em" data-type="string">{{ lang._('Key Type') }}</th> -->
<!--             <th data-column-id="keySize" data-width="20em" data-type="number">{{ lang._('Key Size') }}</th> -->
<!--             <th data-column-id="keyFingerprint" data-type="string">{{ lang._('Key Fingerprint') }}</th> -->
<!--             <th data-column-id="commands" data-width="7em" data-formatter="commands" -->
<!--                 data-sortable="false">{{ lang._('Commands') }}</th> -->
<!--         </tr> -->
<!--         </thead> -->
<!--         <tbody></tbody> -->
<!--         <tfoot> -->
<!--         <tr> -->
<!--             <td></td> -->
<!--             <td> -->
<!--                 <button data-action="add" type="button" class="btn btn-xs btn-primary"> -->
<!--                     <span class="fa fa-fw fa-plus"></span> -->
<!--                 </button> -->
<!--                 <button data-action="deleteSelected" type="button" class="btn btn-xs btn-default"> -->
<!--                     <span class="fa fa-fw fa-trash-o"></span> -->
<!--                 </button> -->
<!--             </td> -->
<!--         </tr> -->
<!--         </tfoot> -->
<!--     </table> -->
<!--     <div class="col-md-12"> -->
<!--         <div id="KPChangeMessage" class="alert alert-info" style="display: none" role="alert"> -->
<!--             {{ lang._('After changing settings, please remember to apply them with the button below') }} -->
<!--         </div> -->
<!--         <hr/> -->
<!--         <button class="btn btn-primary" id="reconfigureAct" -->
<!--                 data-endpoint="/api/ipsec/service/reconfigure" -->
<!--                 data-label="{{ lang._('Apply') }}" -->
<!--                 data-error-title="{{ lang._('Error reconfiguring IPsec') }}" -->
<!--                 type="button" -->
<!--         ></button> -->
<!--         <br/><br/> -->
<!--     </div> -->
<!-- </div> -->

<!-- {{ partial("layout_partials/base_dialog",['fields':general5GSAForm,'id':'Dialog5GSA','label':lang._('Edit Network properties')]) }} -->


