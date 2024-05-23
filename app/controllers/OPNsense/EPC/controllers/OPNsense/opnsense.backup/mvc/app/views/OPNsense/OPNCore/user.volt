{#

Copyright (C) 2023cDigital Solutions
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

<!--suppress BadExpressionStatementJS -->
<script>
//TODO Reconfigure by restarting mme service.
    function saveUsers() {
        $("#saveAct_users_progress").addClass("fa fa-spinner fa-pulse");
        saveFormToEndpoint(url = "/api/opncore/user/addSub", formid = 'frm_user_settings', callback_ok = function () {
            $("#saveAct_users_progress").removeClass("fa fa-spinner fa-pulse");
        }, true);

    }
    function saveProfile() {

        $("#saveAct_profile_progress").addClass("fa fa-spinner fa-pulse");
        saveFormToEndpoint(url = "/api/opncore/profile/addProfile", formid = 'frm_profile_settings', callback_ok = function () {
            $("#saveAct_profile_progress").removeClass("fa fa-spinner fa-pulse");
        }, true);

    }
    //enable IP
    // if ($('#user\\.enabled')[0].checked) {
    //     console.log("HereSA");
    //     enable_ip.removeClass('hidden');
    // }
    $( document ).ready(function() {
        // let data_get_map = {'frm_user_settings': "/api/opncore/user/get"};
        let data_get_map = {'frm_user_settings': "/api/opncore/user/getSub"};
        let data_get_map2 = {'frm_profile_settings': "/api/opncore/profile/get"};
        ShowHideFourGFields()

        mapDataToFormUI(data_get_map).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
            let enable_ip = $('tr[id="row_user.ip]')
            enable_ip.addClass('hidden');
        });

        mapDataToFormUI(data_get_map2).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
        });
        updateServiceControlUI('opncore')

        // Automatically load the started services in the grid
        $('#userList').on('click', function () {
            ajaxCall(url = "/api/opncore/user/searchSub" , sendData = {}, callback = function (data, status) {
                grid_users.bootgrid('reload');
            });

        });
        function ShowHideFourGFields(){
            console.log("HereFirst");
            if ($('#user\\.enabled')[0].checked) {
                console.log("HereF");
                $('tr[id="row_general.enablefiveSA"]').addClass('hidden');
                $('tr[id="row_general.enablefiveNSA"]').addClass('hidden');

            } else {
                console.log("Herethen");
                $('tr[id="row_general.enablefiveSA"]').removeClass('hidden');
                $('tr[id="row_general.enablefiveNSA"]').removeClass('hidden');

            }
        }

        // update history on tab state and implement navigation
        if (window.location.hash !== "") {
            $('a[href="' + window.location.hash + '"]').click()
        }
        $('.nav-tabs a').on('shown.bs.tab', function (e) {
            history.pushState(null, null, e.target.hash);
        });

        $("#grid-user-list").UIBootgrid(
            {   'search':'/api/opncore/user/searchSub',
                'get':'/api/opncore/user/getSub/',
                'set':'/api/opncore/user/setSub/',
                'add':'/api/opncore/user/addSub/',
                'del':'/api/opncore/user/deleteSub/',

            });


        /***********************************************************************
         * link grid actions
         **********************************************************************/

        // let gridParams = {
        //     search:'/api/opncore/user/searchSub',
        //     get:'/api/opncore/user/getSub',
        //     set:'/api/opncore/user/setSub/',
        //     add:'/api/opncore/user/addSub/',
        //     // del:'/api/opncore/user/delUser/',
        //     del:'/api/opncore/user/delSub/',
        // };
        //
        // let gridopt = {
        //     ajax: true,
        //     selection: true,
        //     multiSelect: true,
        //     rowCount:[10,25,50,100,500,1000],
        //     url: '/api/opncore/user/searchSub',
        //     formatters: {
        //         "commands": function (column, row) {
        //             return "<button type=\"button\" title=\"{{ lang._('Edit') }}\" class=\"btn btn-xs btn-default command-edit bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-imsi=\"" + row.imsi + "\"><span class=\"fa fa-pencil\"></span></button> " +
        //                 "<button type=\"button\" title=\"{{ lang._('Delete') }}\" class=\"btn btn-xs btn-default command-delete bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-imsi=\"" + row.imsi + "\"><span class=\"fa fa-trash-o\"></span></button>";
        //         },
        //     },
        // };
        //
        // /**
        //  * reload bootgrid, return to current selected page
        //  */
        // function std_bootgrid_reload(gridId) {
        //     var currentpage = $("#"+gridId).bootgrid("getCurrentPage");
        //     currentpage.bootgrid("reload");
        //     // absolutely not perfect, bootgrid.reload doesn't seem to support when().done()
        //     setTimeout(function(){
        //         $('#'+gridId+'-footer  a[data-page="'+currentpage+'"]').click();
        //     }, 400);
        // }
        //
        // /**
        //  * copy actions for selected items from opnsense_bootgrid_plugin.js
        //  */
        // let grid_users = $("#grid-user-list").bootgrid(gridopt).on("loaded.rs.jquery.bootgrid", function (e)
        // {
        //     // toggle all rendered tooltips (once for all)
        //     $('.bootgrid-tooltip').tooltip();
        //
        //     // scale footer on resize
        //     $(this).find("tfoot td:first-child").attr('colspan',$(this).find("th").length - 1);
        //     $(this).find('tr[data-row-id]').each(function(){
        //         if ($(this).find('[class*="command-toggle"]').first().data("value") === "0") {
        //             $(this).addClass("text-muted");
        //         }
        //     });
        //
        //     // edit dialog id to use
        //     var editDlg = $(this).attr('data-editDialog');
        //     var gridId = $(this).attr('id');
        //
        //     // link delete selected items action
        //     $(this).find("*[data-action=deleteSelected]").click(function(){
        //         if ( gridParams['del'] !== undefined) {
        //             stdDialogConfirm('{{ lang._('Confirm removal') }}',
        //                 '{{ lang._('Do you want to remove the selected item?') }}',
        //                 '{{ lang._('Yes') }}', '{{ lang._('Cancel') }}', function () {
        //                 var rows =$("#"+gridId).bootgrid('getSelectedRows');
        //
        //                 if (rows !== undefined){
        //                     let imsi = $(this).data("row-imsi");
        //                     let uuid = $(this).data("row-uuid");
        //                     var deferreds = [];
        //                     $.each(rows, function(key,imsi){
        //                         deferreds.push(ajaxCall(url='/api/opncore/user/deleteUser/' + uuid , sendData={},null));
        //                     });
        //                     // refresh after load
        //                     $.when.apply(null, deferreds).done(function(){
        //                         std_bootgrid_reload(gridId);
        //                     });
        //                 }
        //             });
        //         } else {
        //             console.log("[grid] action del missing")
        //         }
        //     });
        //
        // });
        //
        // /**
        //  * copy actions for items from opnsense_bootgrid_plugin.js
        //  */
        // grid_users.on("loaded.rs.jquery.bootgrid", function(){
        //
        //     // edit dialog id to use
        //     const editDlg = $(this).attr('data-editDialog');
        //     const gridId = $(this).attr('id');
        //
        //     // edit item
        //     grid_users.find(".command-edit").on("click", function(e)
        //     {
        //         if (editDlg !== undefined && gridParams['get'] !== undefined) {
        //             let uuid = $(this).data("row-id");
        //             let imsi = $(this).data("row-imsi");
        //             console.log(imsi);
        //             console.log(uuid);
        //             let urlMap = {};
        //             urlMap['frm_' + editDlg] = gridParams['get'] + imsi;   //pass the imsi of the row of interest
        //             mapDataToFormUI(urlMap).done(function () {
        //                 // update selectors
        //                 formatTokenizersUI();
        //                 $('.selectpicker').selectpicker('refresh');
        //                 // clear validation errors (if any)
        //                 clearFormValidation('frm_' + editDlg);
        //             });
        //             updateServiceControlUI('opncore')
        //             // show dialog for pipe edit
        //             $('#'+editDlg).modal({backdrop: 'static', keyboard: false});
        //             // define save action
        //             $("#btn_"+editDlg+"_save").unbind('click').click(function(){
        //                 console.log("clicked")
        //                 if (gridParams['set'] !== undefined) {
        //                     saveFormToEndpoint(url=gridParams['set']+imsi,
        //                         formid='frm_' + editDlg, callback_ok=function(){
        //                             $("#"+editDlg).modal('hide');
        //                             std_bootgrid_reload(gridId);
        //                         }, true);
        //                 } else {
        //                     console.log("[grid] action set missing")
        //                 }
        //             });
        //         } else {
        //             console.log("[grid] action get or data-editDialog missing")
        //         }
        //     });
        //
        //     // delete item
        //     grid_users.find(".command-delete").on("click", function(e)
        //     {
        //         if (gridParams['del'] !== undefined) {
        //             var uuid=$(this).data("row-id");
        //             let imsi = $(this).data("row-imsi");
        //             console.log(imsi)
        //             stdDialogConfirm('{{ lang._('Confirm removal') }}',
        //                 '{{ lang._('Do you want to remove the subscriber ') }}' + imsi + '{{ lang._(' ?')}}',
        //                 '{{ lang._('Yes') }}', '{{ lang._('Cancel') }}', function () {
        //                 ajaxCall(url='/api/opncore/user/deleteUser/' + imsi, sendData = {}, callback = function (data, status) {
        //                     updateServiceControlUI('opncore');
        //                     grid_users.bootgrid('reload');
        //                 });
        //             });
        //         } else {
        //             console.log("[grid] action del missing")
        //         }
        //     });
        //
        //
        // });

    });

</script>

<ul class="nav nav-tabs" role="tablist" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#profile"><b>{{ lang._('Profile') }}</b></a></li>
    <li><a data-toggle="tab"  href="#new-user"><b>{{ lang._('New Subscriber') }}</b></a></li>
    <li id="userList"><a data-toggle="tab" href="#user-list"><b>{{ lang._('Subscriber List') }}</b></a></li>

</ul>

<div class="content-box tab-content">


    <div id="profile" class="tab-pane fade in active">
        <div class="col-md-12">
            {{ partial("layout_partials/base_form",['fields':profileForm,'id':'frm_profile_settings'])}}
            <div class="col-md-12 __mt">
                <button class="btn btn-primary" style="display: block" id="saveAct_profile" type="button"
                        onClick="saveProfile()"><b>{{ lang._('Save') }}</b> <i id="saveAct_profile_progress"></i></button>
                <br>

            </div>
        </div>
    </div>
    <div id="new-user" class="tab-pane fade in">
        <div class="col-md-12">
            {{ partial("layout_partials/base_form",['fields':userForm,'id':'frm_user_settings'])}}
            <div class="col-md-12 __mt">
                <button class="btn btn-primary" style="display: block" id="saveAct_users" type="button"
                        onClick="saveUsers()"><b>{{ lang._('Save') }}</b> <i id="saveAct_users_progress"></i></button>
                <br>

            </div>
        </div>
    </div>

    <div id="user-list" class="tab-pane fade">

        <table id="grid-user-list" class="table table-condensed table-hover table-striped table-responsive" data-editDialog="DialogUsers">
            <thead>
            <tr>
                <th data-column-id="imsi" data-type="string">{{ lang._('IMSI') }}</th>
                <th data-column-id="name" data-type="string">{{ lang._('name') }}</th>
<!--                <th data-column-id="opc" data-type="string">{{ lang._('OPC') }}</th>-->
<!--                <th data-column-id="statusCode" data-type="string" data-formatter="accountstatus" data-visible="false">{{ lang._('Status') }}</th>-->
<!--                <th data-column-id="statusLastUpdate" data-type="string" data-formatter="acmestatusdate" data-visible="false">{{ lang._('Registration Date') }}</th>-->
                <th data-column-id="commands" data-width="7em" data-formatter="commands" data-sortable="false">{{ lang._('Commands') }}</th>
                <th data-column-id="uuid" data-type="string" data-identifier="true"  data-visible="false">{{ lang._('ID') }}</th>
            </tr>
            </thead>
            <tbody>
            </tbody>
            <tfoot>
            <tr>
                <td></td>
                <td>
                    <button data-action="deleteSelected" type="button" class="btn btn-xs btn-default"><span class="fa fa-trash-o"></span></button>
                </td>
            </tr>
            </tfoot>
        </table>

    </div>

</div>

{# include dialogs #}
<!--{{ partial("layout_partials/base_dialog",['fields':formDialogAccount,'id':'DialogAccount','label':lang._('Edit Account')])}}-->
{{ partial("layout_partials/base_dialog",['fields':formDialogEditUser,'id':'DialogUsers','label':lang._('Edit Subscriber:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog",['fields':profileForm,'id':'Profile','label':lang._(' Subscriber:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog_processing") }}
