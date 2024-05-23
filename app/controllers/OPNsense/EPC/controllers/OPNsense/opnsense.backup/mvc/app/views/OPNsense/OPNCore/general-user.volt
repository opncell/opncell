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

    $(document).ready(function () {
        let data_get_map = {'frm_user_settings': "/api/opncore/user/getss"};
        mapDataToFormUI(data_get_map).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
        });
        updateServiceControlUI('opncore');

        $("#grid-user-list").UIBootgrid({
            'search':'/api/opncore/user/fetchUsers',
            'get':'api/opncore/user/getUser',
            'set':'api/opncore/user/getUser',
        });


        // Automatically load the started services in the grid
        $('#userList').on('click', function () {
            ajaxCall(url = "/api/opncore/user/fetchUsers", sendData = {}, callback = function (data, status) {

                $('#grid-user-list').bootgrid('reload');

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

    function saveUsers() {
        $("#saveAct_users_progress").addClass("fa fa-spinner fa-pulse");
        saveFormToEndpoint(url = "/api/opncore/user/set", formid = 'frm_user_settings', callback_ok = function () {

            $("#saveAct_users_progress").removeClass("fa fa-spinner fa-pulse");
        }, true);

    }


</script>

<!-- Navigation bar -->
<ul class="nav nav-tabs" data-tabs="tabs" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#new-user">{{ lang._('New User') }}</a></li>
    <li id="userList"><a data-toggle="tab" href="#user-list">{{ lang._('Subscriber List') }}</a></li>
</ul>
<div class="col-md-6 __mt">
    <div id="restartServices" class="alert alert-dismissible alert-info" style="display: none" role="alert">
        {{ lang._('Changes have been made, and services restarted.') }}
    </div>
</div>
<div class="content-box tab-content">
    <div id="new-user" class="tab-pane fade in active">
        <div class="content-box" style="padding-bottom: 1.5em;">
            {{ partial("layout_partials/base_form",['fields':userForm,'id':'frm_user_settings'])}}
            <div class="col-md-12 __mt">
                <button class="btn btn-primary" style="display: block" id="saveAct_users" type="button"
                        onClick="saveUsers()"><b>{{ lang._('Save') }}</b> <i id="saveAct_users_progress"></i></button>
                <br>

            </div>
        </div>
    </div>


    <div id="user-list" class="tab-pane fade in">
        <table id="grid-user-list" class="table table-condensed table-hover table-striped table-responsive"
               data-editDialog="DialogUsers">

            <thead>
            <tr>
                <th data-column-id="imsi" data-type="string" data-sortable="false" data-visible="true">
                    {{ lang._('IMSI') }}
                </th>
                <th data-column-id="apn" data-type="string" data-identifier="true" data-visible="true">{{
                    lang._('APN') }}
                </th> <th data-column-id="opc" data-type="string" data-identifier="true" data-visible="false">{{
                lang._('OPC') }}
            </th>

                <th data-column-id="commands" data-formatter="commands" data-sortable="false">{{
                    lang._('Edit') }}
                </th>

            </tr>
            </thead>
            <tbody>

            </tbody>
        </table>
    </div>
</div>
{{ partial("layout_partials/base_dialog",['fields':formDialogEditUser,'id':'DialogUsers','label':lang._('User Management:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog_processing") }}
<hr>

<script>
    //
    // if (!$("#grid-user-list").hasClass('bootgrid-table')) {
    //     var grid_alerts = $("#grid-user-list").UIBootgrid({
    //         search: '/api/opncore/user/fetchUsers',
    //         get: '/api/ids/service/getAlertInfo/',
    //         options: {
    //             multiSelect: false,
    //             selection: false,
    //             rowCount: [7, 50, 100, 250, 500, 1000, 5000],
    //             requestHandler: addUserFilters,
    //             labels: {
    //                 infos: "{{ lang._('Showing %s to %s') | format('{{ctx.start}}','{{ctx.end}}') }}"
    //             },
    //             formatters: {
    //                 info: function (column, row) {
    //                     return "<button type=\"button\" class=\"btn btn-xs btn-default command-alertinfo bootgrid-tooltip\" title=\"{{ lang._('View') }}\" data-row-id=\"" + row.filepos + "/" + row.fileid + "\"><span class=\"fa fa-pencil fa-fw\"></span></button> ";
    //                 }
    //             },
    //         }
    //     });
    // }
    //
    // /**
    //  * link query alerts button.
    //  */
    // $("#actQueryAlerts").click(function(){
    //     $('#grid-user-list').bootgrid('reload');
    // });
    // $("#inputSearchAlerts").keypress(function (e) {
    //     if (e.which === 13) {
    //         $("#actQueryAlerts").click();
    //     }
    // });
    //
    //     function addUserFilters(request) {
    //         var search_phrase = $("#inputSearchAlerts").val();
    //         console.log(search_phrase)
    //
    //         // // add loading overlay
    //         // $('#processing-dialog').modal('show');
    //         // $("#grid-user-list").bootgrid().on("loaded.rs.jquery.bootgrid", function (e) {
    //         //     $('#processing-dialog').modal('hide');
    //         // });
    //
    //         request['searchPhrase'] = search_phrase;
    //         return request;
    //     }
    // // tooltip wide fields in alert grid
    // grid_alerts.on("loaded.rs.jquery.bootgrid", function(){
    //     $("#grid-alerts-header-extra").children().each(function(){
    //         $(this).prependTo($("#grid-alerts-header > .row > .actionBar"));
    //     });
    //     $("#grid-alerts-header > .row > .actionBar > .search.form-group:last").hide();
    //     $("#grid-alerts-header > .row > .actionBar > .actions.btn-group > .btn.btn-default").hide();
    //     $("#grid-alerts > tbody > tr > td").each(function(){
    //         if ($(this).outerWidth() < $(this)[0].scrollWidth) {
    //             var grid_td = $("<span/>");
    //             grid_td.html($(this).html());
    //             grid_td.tooltip({title: $(this).text()});
    //             $(this).html(grid_td);
    //         }
    //     });
    // });
    // hook in alert details on alertinfo command
    // grid_alerts.on("loaded.rs.jquery.bootgrid", function(){
    //     grid_alerts.find(".command-alertinfo").on("click", function(e) {
    //         var uuid=$(this).data("row-id");
    //         ajaxGet('/api/ids/service/getAlertInfo/' + uuid, {}, function(data, status) {
    //             if (status == 'success') {
    //                 ajaxGet("/api/ids/settings/getRuleInfo/"+data['alert_sid'], {}, function(rule_data, rule_status) {
    //                     var tbl = $('<table class="table table-condensed table-hover ids-alert-info"/>');
    //                     var tbl_tbody = $("<tbody/>");
    //                     var alert_fields = {};
    //                     alert_fields['timestamp'] = "{{ lang._('Timestamp') }}";
    //                     alert_fields['alert'] = "{{ lang._('Alert') }}";
    //                     alert_fields['alert_sid'] = "{{ lang._('Alert sid') }}";
    //                     alert_fields['proto'] = "{{ lang._('Protocol') }}";
    //                     alert_fields['src_ip'] = "{{ lang._('Source IP') }}";
    //                     alert_fields['dest_ip'] = "{{ lang._('Destination IP') }}";
    //                     alert_fields['src_port'] = "{{ lang._('Source port') }}";
    //                     alert_fields['dest_port'] = "{{ lang._('Destination port') }}";
    //                     alert_fields['in_iface'] = "{{ lang._('Interface') }}";
    //                     alert_fields['http.hostname'] = "{{ lang._('http hostname') }}";
    //                     alert_fields['http.url'] = "{{ lang._('http url') }}";
    //                     alert_fields['http.http_user_agent'] = "{{ lang._('http user_agent') }}";
    //                     alert_fields['http.http_content_type'] = "{{ lang._('http content_type') }}";
    //                     alert_fields['tls.subject'] = "{{ lang._('tls subject') }}";
    //                     alert_fields['tls.issuerdn'] = "{{ lang._('tls issuer') }}";
    //                     alert_fields['tls.session_resumed'] = "{{ lang._('tls session resumed') }}";
    //                     alert_fields['tls.fingerprint'] = "{{ lang._('tls fingerprint') }}";
    //                     alert_fields['tls.serial'] = "{{ lang._('tls serial') }}";
    //                     alert_fields['tls.version'] = "{{ lang._('tls version') }}";
    //                     alert_fields['tls.notbefore'] = "{{ lang._('tls notbefore') }}";
    //                     alert_fields['tls.notafter'] = "{{ lang._('tls notafter') }}";
    //
    //                     $.each( alert_fields, function( fieldname, fielddesc ) {
    //                         var data_ptr = data;
    //                         $.each(fieldname.split('.'),function(indx, keypart){
    //                             if (data_ptr != undefined) {
    //                                 data_ptr = data_ptr[keypart];
    //                             }
    //                         });
    //
    //                         if (data_ptr != undefined) {
    //                             var row = $("<tr/>");
    //                             row.append($("<td/>").text(fielddesc));
    //                             if (fieldname == 'in_iface' && interface_descriptions[data_ptr.replace(/\+$/, '')] != undefined) {
    //                                 row.append($("<td/>").text(interface_descriptions[data_ptr.replace(/\+$/, '')]));
    //                             } else {
    //                                 row.append($("<td/>").text(data_ptr));
    //                             }
    //                             tbl_tbody.append(row);
    //                         }
    //                     });
    //
    //                     if (rule_data.action != undefined) {
    //                         var alert_select = $('<select/>');
    //                         var alert_enabled = $('<input type="checkbox"/>');
    //                         if (rule_data.enabled == '1') {
    //                             alert_enabled.prop('checked', true);
    //                         }
    //                         $.each(rule_data.action, function(key, value){
    //                             var opt = $('<option/>').attr("value", key).text(value.value);
    //                             if (value.selected == 1) {
    //                                 opt.attr('selected', 'selected');
    //                             }
    //                             alert_select.append(opt);
    //                         });
    //                         tbl_tbody.append(
    //                             $("<tr/>").append(
    //                                 $("<td/>").text("{{ lang._('Configured action') }}"),
    //                                 $("<td id='alert_sid_action'/>").append(
    //                                     alert_enabled, $("<span/>").html("&nbsp; <strong>{{lang._('Enabled')}}</strong><br/>"), alert_select, $("<br/>")
    //                                 )
    //                             )
    //                         );
    //                         alert_select.change(function(){
    //                             var rule_params = {'action': alert_select.val()};
    //                             if (alert_enabled.is(':checked')) {
    //                                 rule_params['enabled'] = 1;
    //                             } else {
    //                                 rule_params['enabled'] = 0;
    //                             }
    //                             ajaxCall("/api/ids/settings/setRule/"+data['alert_sid'], rule_params, function() {
    //                                 $("#alert_sid_action > small").remove();
    //                                 $("#alert_sid_action").append($('<small/>').html("{{ lang._('Changes will be active after apply (rules tab)') }}"));
    //                             });
    //                         });
    //                         alert_enabled.change(function(){
    //                             alert_select.change();
    //                         });
    //                     }
    //                     if (data['payload_printable'] != undefined && data['payload_printable'] != null) {
    //                         tbl_tbody.append(
    //                             $("<tr/>").append(
    //                                 $("<td colspan=2/>").append(
    //                                     $("<strong/>").text("{{ lang._('Payload') }}")
    //                                 )
    //                             )
    //                         );
    //
    //                         var row = $("<tr/>");
    //                         row.append( $("<td colspan=2/>").append($("<pre style='width:1100px'/>").html($("<code/>").text(data['payload_printable']))));
    //                         tbl_tbody.append(row);
    //                     }
    //
    //                     tbl.append(tbl_tbody);
    //                     stdDialogInform("{{ lang._('Alert info') }}", tbl, "{{ lang._('Close') }}", undefined, "info", 'suricata-alert');
    //                     alert_select.selectpicker('refresh');
    //                 });
    //             }
    //         });
    //     }).end();
    // });

</script>
