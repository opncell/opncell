{#

Copyright (C) 2026 Digital Solutions
Copyright (C) 2026 Wireless Laboratories, Inc
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

<ul class="nav nav-tabs" data-tabs="tabs" id="maintabs">
    <li id="ProfileList" class="active"><a data-toggle="tab" href="#profile-list"><b>{{ lang._('Profile List')
        }}</b></a></li>
    <li id="userList"><a data-toggle="tab" href="#user-list"><b>{{ lang._('Subscriber List') }}</b></a></li>
    <li id="hnetTab"><a data-toggle="tab" href="#hnet"><b>{{ lang._('Hnet') }}</b></a></li>
    <li id="bulk"><a data-toggle="tab" href="#bulkinsert"><b>{{ lang._('Bulk Insertion') }}</b></a></li>

</ul>
<div class="tab-content content-box">
    <div class="col-md-8 __mt">
        <div id="file_uploaded" class="alert alert-dismissible alert-info" style="display: none" role="alert">
            {{ lang._('Successfully uploaded file.') }}<br>
            {{ lang._('Next Step: Select a profile to which subscribers will be attached .') }}
        </div>
        <div id="duplicates" class="alert alert-dismissible alert-info" style="display: none" role="alert">
            {{ lang._('Subscribers added. Duplicates that were detected have been skipped') }}<br>

        </div>
        <div id="success" class="alert alert-dismissible alert-info" style="display: none" role="alert">
            {{ lang._('Successfully added subscribers.') }}<br>

        </div>
        <div id="no_file" class="alert alert-dismissible alert-info" style="display: none" role="alert">
            {{ lang._('No file detected. Kindly attach a file') }}<br>
        </div>
        <div id="format_not_supported" class="alert alert-dismissible alert-info" style="display: none" role="alert">
            {{ lang._('File format not supported. Please upload either a .CSV or .INC file') }}<br>
        </div>
    </div>
    <div id="bulkinsert" class="tab-pane fade in">
        <div class="col-md-12">
            <h3>{{ lang._('- For bulk insertion of users, use file upload. Allowed file formats are .inc or .csv
                file. Below is a template for what an expected file SHOULD look like')}}<br/></h3>
            <h3>{{ lang._('-  Below is a template for what the expected file SHOULD look like')}}<br/></h3>

            <table class="table table-condensed table-bordered">
                <thead>
                <tr>
                    <th>imsi</th>
                    <th>ki</th>
                    <th>opc</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <td>9997080930195106</td>
                    <td>1c59cca0c8b14605944fe3d6c1037b85</td>
                    <td>789403E75282063E5B3C52FE823077C919</td>
                </tr>
                </tbody>
            </table>
            <br>
            <form method="post" id="uploadForm" enctype="multipart/form-data">
                <input type="file" name="file" id="fileInput">
                <br>
                <button class="btn btn-primary" type="submit" onclick="uploadFile()">{{ lang._('Upload') }}<b><i
                        id="saveAct_upload_progress"></i></b></button>
            </form>

            <br>
            {{ partial("layout_partials/base_form",['fields':bulkForm,'id':'frm_bulk_settings'])}}
            <br>
            <button class="btn btn-primary" style="display: block" id="saveBulkAct_users" type="button"
                    onClick="saveBulkUsers()"><b>{{ lang._('Save') }}</b> <i id="saveBulkAct_users_progress"></i>
            </button>
            <br>
        </div>
    </div>

    <div id="user-list" class="tab-pane fade in">
        <div class="col-md-12 __mt">
            <div id="failedSave" class="alert alert-dismissible alert-info" style="display: none" role="alert">
                {{ lang._('Subscriber not added') }}<br>
            </div>
            <div id="Error" class="alert alert-dismissible alert-info" style="display: none" role="alert">
                {{ lang._('A db Error occured. Check if the db is up and running, then try again.') }}<br>
            </div>
            <div id="successfulSave" class="alert alert-dismissible alert-info" style="display: none" role="alert">
                {{ lang._('Subscriber added.') }}<br>
            </div>
        </div>
        <div class="col-md-12 __mt">
            <div  id="failedDelete" class="alert alert-dismissible alert-info" style="display: none" role="alert">
                {{ lang._('Subscriber not deleted.') }}
            </div>
            <div id="successfulDelete" class="alert alert-dismissible alert-info" style="display: none" role="alert">
                {{ lang._('Subscriber deleted successfully') }}
            </div>
        </div>
        <div class="col-md-3 __mt">
            <div id="deleting" class="alert alert-dismissible alert-danger" style="display: none" role="alert">
                {{ lang._('Deleting.......') }}
            </div>
        </div>
        <!--        <button class="btn btn-danger" style="display: none;  float: left; margin-right: 78px;text-align: center" id="deleting" type="button">-->
        <!--            <b>{{ lang._('Deleting....') }}</b> <i id="deleting_progress"></i>-->
        <!--        </button>-->

        <table id="grid-user-list" class="table table-condensed table-hover table-striped table-responsive"
               data-editDialog="DialogUsers" data-addDialog="DialogAddUsers">
            <thead>
            <tr>
                <th data-column-id="imsi" data-type="string" data-visible="true" >{{ lang._('IMSI') }}</th>
                <th data-column-id="profile" data-type="string" data-visible="true" >{{ lang._('Profile') }}</th>
                <th data-column-id="commands" data-width="7em" data-formatter="commands" >{{
                    lang._('Commands') }}
                </th>
                <th data-column-id="uuid" data-type="string" data-identifier="true" data-visible="false">{{ lang._('ID')
                    }}
                </th>
            </tr>
            </thead>
            <tbody>
            </tbody>
            <tfoot>
            <tr>
<!--                <td>-->
<!--                    <button data-action="deleteSelected" type="button" class="btn btn-xs btn-default"><span-->
<!--                            class="fa fa-trash-o"></span></button>-->
<!--                </td>-->
                <td>
                    <button type="button" class="btn btn-xs btn-default command-add"><span
                            class="fa fa-plus"></span></button>
                </td>

            </tr>
            </tfoot>
        </table>
    </div>
    <div id="profile-list" class="tab-pane fade in active">
        <table id="grid-profile-list" class="table table-condensed table-hover table-striped table-responsive"
               data-editDialog="DialogProfile">
            <thead>
            <tr>
                <th data-column-id="apn" data-type="string" data-visible="true" data-sortable="true">{{ lang._('Name') }}</th>
                <th data-column-id="count" data-type="string" data-visible="true" data-sortable="true">{{ lang._('Subscribed users') }}</th>
                <th data-column-id="commands" data-width="7em" data-formatter="commands" data-sortable="false">{{
                    lang._('Commands') }}
                </th>
                <th data-column-id="uuid" data-type="string" data-identifier="true" data-visible="false">{{ lang._('ID')
                    }}
                </th>
            </tr>
            </thead>
            <tbody>
            </tbody>
            <tfoot>
            <tr>
                <td></td>
                <td>
                    <button type="button" class="btn btn-xs btn-default command-add"><span
                            class="fa fa-plus"></span></button>
                </td>
            </tr>
            </tfoot>
        </table>

    </div>

    <!-- Hnet Tab -->
    <div id="hnet" class="tab-pane fade in">
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
                    <button class="btn btn-primary __ml" id="generateAct_hnet" type="button">
                        <b>{{ lang._('Generate New Key') }}</b>
                        <i id="generateAct_hnet_progress"></i>
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
            </div>

            <div class="modal-body">
                <div class="content-box">
                    <hr>
                    <div class="form-group">
                        &nbsp;&nbsp;<label>Hnet ID</label>
                        &nbsp;&nbsp;<div class="well well-sm" id="hnet_id"></div>
                    </div>

                    <!-- Private Key Path -->
                    <div class="form-group">
                        &nbsp;&nbsp;<label>Private Key Path</label>
                        &nbsp;&nbsp;<div class="well well-sm" id="hnet_result_priv_path"></div>
                    </div>

                    <!-- Public Key Path -->
                    <div class="form-group">
                        &nbsp;&nbsp;<label>Public Key Path (PEM)</label>
                        &nbsp;&nbsp;<div class="well well-sm" id="hnet_result_path"></div>
                    </div>

                    <div class="row __mt">
                        <div class="col-md-12 __ml">
                            &nbsp;&nbsp;<div class="well well-sm" style="word-break: break-all; display: none" id="hnet_result_hex"></div>
                            &nbsp;&nbsp;<button class="btn btn-primary" id="copy_hex_btn">
                                <i class="fa fa-copy"></i> Copy HEX
                            </button>
                            &nbsp;&nbsp;<div class="well well-sm" style="word-break: break-all; display: none" id="hnet_result_pem"></div>
                            &nbsp;&nbsp;<button class="btn btn-primary" id="copy_pem_btn">
                                <i class="fa fa-copy"></i> Copy PEM
                            </button>
                        </div>
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

<!-- HNET Existing Keys Modal -->
<div id="hnetListModal" class="modal fade" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">

            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="fa fa-list fa-fw"></i>
                    {{ lang._('Existing Hnet Keys') }}
                </h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>

            <div class="modal-body">
                <p>{{ lang._(' Reuse an existing Hnet ID\'s public key when provisioning new USIMs, or reactivate 5G SA using the keys already configured.') }}</p>
                <table class="table table-condensed table-striped">
                    <thead>
                        <tr>
                            <th>{{ lang._('ID') }}</th>
                            <th>{{ lang._('Scheme') }}</th>
                            <th>{{ lang._('Private Key Path') }}</th>
                            <th>{{ lang._('Public Key') }}</th>
                        </tr>
                    </thead>
                    <tbody id="hnet_list_body"></tbody>
                </table>
            </div>

            <div class="modal-footer">
                <button type="button" class="btn btn-warning" id="activate_existing_hnet">
                    {{ lang._('Activate 5G SA With Existing Keys') }}
                </button>
                <button type="button" class="btn btn-primary" data-dismiss="modal">
                    {{ lang._('Close') }}
                </button>
            </div>

        </div>
    </div>
</div>
<script>

    //TODO Reconfigure by restarting mme service.
    function saveUsers() {
        $("#saveAct_users_progress").addClass("fa fa-spinner fa-pulse");
        saveFormToEndpoint(url = "/api/opncell/user/addSub", formid = 'frm_user_settings', callback_ok = function (data, status) {
            $("#saveAct_users_progress").removeClass("fa fa-spinner fa-pulse");
            console.log(data.result)

        }, true);

    }

    function saveBulkUsers() {

        $("#saveBulkAct_users_progress").addClass("fa fa-spinner fa-pulse");

        saveFormToEndpoint(url = "/api/opncell/bulk/addBulkSub", formid = 'frm_bulk_settings', callback_ok = function (data) {
            console.log(data.uuid)
            ajaxCall(url = "/api/opncell/bulk/saveBulkUsers/" + data.uuid, sendData = {}, callback = function (data, status) {
                console.log(data)
                $("#saveBulkAct_users_progress").removeClass("fa fa-spinner fa-pulse");
                $("#file_uploaded").attr("style", "display:none");
                $("#no_file").attr("style", "display:none");
                if(data.length > 0 ){
                    $("#duplicates").attr("style", "display:block");
                    fadeOut("#duplicates")
                } else {
                    $("#success").attr("style", "display:block");
                    fadeOut("#success")
                }


            });

        }, true);

    }

    function saveProfile() {
        $("#saveAct_profile_progress").addClass("fa fa-spinner fa-pulse");
        saveFormToEndpoint(url = "/api/opncell/profile/addProfile", formid = 'frm_profile_settings', callback_ok = function () {
            $("#saveAct_profile_progress").removeClass("fa fa-spinner fa-pulse");
        }, true);

    }

    function fadeOut(strings) {
        setTimeout(function() {
            $(strings).fadeOut("slow");
        }, 5000);

    }


    let globalFileContent;

    function uploadFile() {

        $('#uploadForm').submit(function (event) {
            event.preventDefault(); // Prevent default form submission
            $("#saveAct_upload_progress").addClass("fa fa-spinner fa-pulse");

            var formData = new FormData();
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            formData.append('file', file);

            $.ajax({
                type: 'POST',
                url: '/api/opncell/user/upload',
                data: formData,
                processData: false, // Don't process the data
                contentType: false, // Don't set content type (let jQuery decide)
                success: function (response) {
                    console.log('Response from server:', response);
                    if(response.result === 'failed'){

                        $("#no_file").attr("style", "display:block");
                        fadeOut("#no_file")
                        $("#format_not_supported").attr("style", "display:none");
                        $("#saveAct_upload_progress").removeClass("fa fa-spinner fa-pulse");
                    } else if(response['result'] === 'Unsupported Format') {
                        $("#format_not_supported").attr("style", "display:block");
                        fadeOut("#format_not_supported")
                        $("#saveAct_upload_progress").removeClass("fa fa-spinner fa-pulse");
                    }
                    else {
                        globalFileContent = response;
                        $("#no_file").attr("style", "display:none");
                        $("#format_not_supported").attr("style", "display:none");
                        $("#file_uploaded").attr("style", "display:block");
                        fadeOut("#file_uploaded")
                        $("#saveAct_upload_progress").removeClass("fa fa-spinner fa-pulse");
                    }

                },
                error: function (xhr, status, error) {
                    console.error('Error:', error);
                }
            });

        });
    }



    $(document).ready(function () {
        const network = localStorage.getItem("networkName");
        console.log(network);

        let data_get_map = {'formDialogAddUser': "/api/opncell/user/getSub"};
        let data_get_map2 = {'frm_profile_settings': "/api/opncell/profile/getProfile"};
        let data_get_map3 = {'frm_bulk_settings': "/api/opncell/bulk/get"};

        mapDataToFormUI(data_get_map).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
        });

        mapDataToFormUI(data_get_map2).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
        });
        mapDataToFormUI(data_get_map3).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
        });
        updateServiceControlUI('opncell')

        // Automatically load the subscribers in the table
        $('#userList').on('click', function () {
            ajaxCall(url = "/api/opncell/user/searchSub", sendData = {}, callback = function (data, status) {
                $("#grid-user-list").bootgrid('reload');
            });

        });
        // Automatically load the subscribers in the table
        $('#ProfileList').on('click', function () {
            console.log("profile")
            ajaxCall(url = "/api/opncell/profile/searchProfile", sendData = {}, callback = function (data, status) {
                $("#grid-profile-list").bootgrid('reload');
            });

        });

        // update history on tab state and implement navigation
        if (window.location.hash !== "") {
            $('a[href="' + window.location.hash + '"]').click()
        }
        $('.nav-tabs a').on('shown.bs.tab', function (e) {
            history.pushState(null, null, e.target.hash);
        });

        // Manually doing the tables --For customization --User Edition
        let gridParams = {
            search: '/api/opncell/user/searchSub',
            // get: '/api/opncell/user/editSub/',
            get: '/api/opncell/user/getSub/',
            set: '/api/opncell/user/setSub/',
            add: '/api/opncell/user/addSub/',
            del: '/api/opncell/user/deleteSub/',
           toggle:'',
        };

        let gridOptions = $("#grid-user-list").UIBootgrid({
            ajax: true,
            selection: false,
            multiSelect: false,
            rowCount: [10, 25, 50, 100, 500, 1000],
            search: '/api/opncell/user/searchSub',
            get: '/api/opncell/user/getSub/',
            set: '/api/opncell/user/setSub/',
            add: '/api/opncell/user/addSub/',
            del: '/api/opncell/user/deleteSub/',
            toggle:'',

            options: {
                formatters: {
                    "commands": function (column, row) {
                        return "<button type=\"button\" title=\"{{ lang._('Edit Profile') }}\" class=\"btn btn-xs btn-default command-edit bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-imsi=\"" + row.imsi + "\"><span class=\"fa fa-pencil\"></span></button> " +
                            "<button type=\"button\" title=\"{{ lang._('Delete user') }}\" class=\"btn btn-xs btn-default command-delete bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-imsi=\"" + row.imsi + "\"><span class=\"fa fa-trash-o\"></span></button>";
                    },
                }
            }

        });

        /**
         * copy actions for selected items from opnsense_bootgrid_plugin.js User Edition
         */
        gridOptions.on("loaded.rs.jquery.bootgrid", function (e) {

            $(this).find(".command-add").off('click');
            $(this).find(".command-edit").off('click');
            $(this).find(".command-delete").off('click');
            $(this).find("*[data-action=deleteSelected]").off('click')
            $(this).find(".command-enable-selected").remove()
            $(this).find(".command-disable-selected").remove()

            // add a new user
            $(this).find(".command-add").on('click' ,function () {
            console.log("clicked add button")
                if (gridParams['add'] !== undefined) {
                    var urlMap = {};
                    urlMap['frm_' + 'DialogAddUsers'] = gridParams['get'];
                    mapDataToFormUI(urlMap).done(function () {
                        // update selectors
                        formatTokenizersUI();
                        $('.selectpicker').selectpicker('refresh');
                        // clear validation errors (if any)
                        clearFormValidation('frm_' + 'DialogAddUsers');
                    });

                    $('#' + 'DialogAddUsers').modal({backdrop: 'static', keyboard: false});
                    //
                    $("#btn_" + 'DialogAddUsers' + "_save").unbind('click').click(function () {
                        saveFormToEndpoint(url = "/api/opncell/user/addSub",
                            formid = 'frm_' + 'DialogAddUsers', callback_ok = function (data) {
                                console.log(data.result)
                                console.log(data)
                                $("#" + 'DialogAddUsers').modal('hide');
                               gridOptions.bootgrid("reload");
                                if (data.result === "failed") {
                                    $("#failedSave").attr("style", "display:block");
                                    fadeOut("#failedSave")
                                } else if(data.result === "saved"  || data.result === "Success" ) {
                                    $("#successfulSave").attr("style", "display:block");
                                    fadeOut("#successfulSave")
                                } else {
                                    $("#Error").text("The following DB error occured: " + data.result)
                                        .attr("style", "display:block");
                                    fadeOut("#Error")
                                }
                            }, true);
                    });
                }
                else {
                    console.log("[grid] action add missing")
                }
            });

            // delete user
            $(this).find(".command-delete").on("click", function (e) {
                if (gridParams['del'] !== undefined) {
                    var uuid = $(this).data("row-id");
                    let imsi = $(this).data("row-imsi");
                    stdDialogConfirm("{{ lang._('Confirm Subscriber Removal') }}", "{{ lang._('Do you want to remove the subscriber') }}" + "{{ lang._('""')}}" + imsi + "{{ lang._('"
                    "')}}" + "{{ lang._(' ? ')}}", "{{ lang._('Yes') }}", "{{ lang._('Cancel') }}", function (data, status) {
                        $("#deleting").attr("style", "display:block");
                        fadeOut("#deleting")
                        $("#deleting_progress").addClass("fa fa-spinner fa-pulse");
                        ajaxCall(url = "/api/opncell/user/deleteSubFromDB/"  + imsi, sendData = {}, callback = function (data, status) {
                            if (data.result === "failed"){
                                $("#deleting").attr("style", "display:none");
                                $("#failedDelete").attr("style", "display:block");
                                fadeOut("#failedDelete")

                            } else {
                                $("#deleting").attr("style", "display:none");
                                $("#successfulDelete").attr("style", "display:block");
                                fadeOut("#successfulDelete")
                            }
                            console.log(data.result)
                            updateServiceControlUI('opncell');
                           gridOptions.bootgrid('reload');
                            $("#successfulDelete").attr("style", "display:none");
                            $("#failedDelete").attr("style", "display:none");
                        });
                    }
                )
                } else {
                    console.log("[grid] action del missing")
                }
            });

           //Attach/replace/change a profile to existing user
            $(this).find(".command-edit").on("click", function (e) {
                // edit dialog id to use
                if (gridOptions['get'] !== undefined) {
                    let imsi = $(this).data("row-imsi");
                    let urlMap = {};

                    urlMap['frm_' + 'DialogUsers'] = '/api/opncell/profile/getSingleSub/' + imsi;   //pass the imsi of the row of interest
                    mapDataToFormUI(urlMap).done(function () {
                        // update selectors
                        formatTokenizersUI();
                        $('.selectpicker').selectpicker('refresh');
                        // clear validation errors (if any)
                        clearFormValidation('frm_' + 'DialogUsers');
                    });
                    updateServiceControlUI('opncell')
                    // show dialog for pipe edit
                    $('#' + 'DialogUsers').modal({backdrop: 'static', keyboard: false});
                    // define save action
                    $("#btn_" + 'DialogUsers' + "_save").unbind('click').click(function () {
                        $("#btn_" + 'DialogUsers' + "_save").append('<i id="saveBulkAct_users_progress"></i>').addClass("fa fa-spinner")
                        if (gridParams['set'] !== undefined) {
                            saveFormToEndpoint(url = "/api/opncell/user/setSub/" + imsi, formid = 'frm_' + 'DialogUsers', callback_ok = function (data) {
                                $("#" + 'DialogUsers').modal('hide');
                                gridOptions.bootgrid("reload");
                                console.log(data)
                                $("#btn_" + 'DialogUsers' + "_save").append('<i id="saveBulkAct_users_progress"></i>').removeClass("fa fa-spinner")
                                // $("#saveAct_configs_progress").addClass("fa fa-spinner fa-pulse");
                                ajaxCall(url = "/api/opncell/service/reconfigureAct/" + network, sendData = {}, callback = function (data, status) {
                                    updateServiceControlUI('opncell');

                                    // $("#saveAct_configs_progress").removeClass("fa fa-spinner fa-pulse");

                                });
                            }, true);
                        } else {
                            console.log("[grid] action set missing")
                        }
                    });
                } else {
                    console.log("[grid] action get or data-editDialog missing")
                }
            });

            $(this).find("*[data-action=deleteSelected]").on('click', function () {

                console.log("clicked");
                if (gridParams['del'] !== undefined) {
                    stdDialogConfirm('{{ lang._("Confirm User removal") }}', '{{ lang._("Do you want to remove the selected users ? ") }}', '{{ lang._("Yes") }}', '{{ lang._("Cancel") }}', function () {
                            var rows = gridOptions.bootgrid('getSelectedRows');
                            console.log(rows);
                            if (rows !== undefined) {
                                let imsi = $(this).data("row-imsi");
                                let uuid = $(this).data("row-uuid");
                                var deferreds = [];
                                $.each(rows, function (key, uuid) {
                                    deferreds.push(ajaxCall(url = '/api/opncell/user/deleteSub/' + uuid, sendData = {}, null));
                                });
                                // refresh after load
                                $.when.apply(null, deferreds).done(function () {
                                    std_bootgrid_reload(gridOptions);

                                });
                            } else {
                                console.log("undefined")
                            }
                        }
                    )

                } else {
                    console.log("[grid] action del missing")
                }
            });

        });

        /**
         * copy actions for selected items from opnsense_bootgrid_plugin.js
         */

        // Manually doing the table for subscribers--For customization ---Profile Edition
        let gridProfileParams = {
                search: '/api/opncell/profile/searchProfile',
                get: '/api/opncell/profile/editProfile/',
                set: '/api/opncell/profile/setProfile/',
                add: '/api/opncell/profile/addProfile/',
                del: '/api/opncell/profile/deleteProfile/',
                toggle:'',
            };

        let gridProfileOptions = $("#grid-profile-list").UIBootgrid({
            ajax: true,
            selection: true,
            multiSelect: false,
            rowCount: [10, 25, 50, 100, 500, 1000],
            search: '/api/opncell/profile/searchProfile',
            get: '/api/opncell/profile/editProfile/',
            set: '/api/opncell/profile/setProfile/',
            add: '/api/opncell/profile/addProfile/',
            del: '/api/opncell/profile/deleteProfile/',
            toggle:'',
            options: {
                formatters: {
                    "commands": function (column, row) {
                        return "<button type=\"button\" title=\"{{ lang._('Edit profile') }}\" class=\"btn btn-xs btn-default command-edit bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-count=\"" + row.count + "\" data-row-imsi=\"" + row.imsi + "\"><span class=\"fa fa-pencil\"></span></button> " +
                            "<button type=\"button\" title=\"{{ lang._('Delete Profile') }}\" class=\"btn btn-xs btn-default command-delete bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-count=\"" + row.count + "\" data-row-name=\"" + row.apn + "\"><span class=\"fa fa-trash-o\"></span></button>";
                    }
                }
            }
        });


        /**
         * copy actions for selected items from opnsense_bootgrid_plugin.js
         */
        // edit profile dialog
        gridProfileOptions.on("loaded.rs.jquery.bootgrid", function (e) {

            // toggle all rendered tooltips (once for all)
            $('.bootgrid-tooltip').tooltip();

            $(this).find("*[data-action=add]").off('click');
            $(this).find(".command-edit").off('click');
            $(this).find(".command-delete").off('click');
            $(this).find("*[data-action=deleteSelected]").off('click')
            $(this).find(".command-enable-selected").remove()
            $(this).find(".command-disable-selected").remove()


            // link Add new to child button with data-action = add
            $(this).find(".command-add").click(function () {
                console.log("clicked profile add")
                if (gridProfileParams['get'] !== undefined && gridProfileParams['add'] !== undefined) {
                    var urlMap = {};
                    urlMap['frm_' + 'DialogProfile'] = gridProfileParams['get'];
                    mapDataToFormUI(urlMap).done(function () {
                        // update selectors
                        formatTokenizersUI();
                        $('.selectpicker').selectpicker('refresh');
                        // clear validation errors (if any)
                        clearFormValidation('frm_' + 'DialogProfile');
                    });

                    $('#' + 'DialogProfile').modal({backdrop: 'static', keyboard: false});
                    //
                    $("#btn_" + 'DialogProfile' + "_save").unbind('click').click(function () {
                        saveFormToEndpoint(url = gridProfileParams['add'],
                            formid = 'frm_' + 'DialogProfile', callback_ok = function () {
                                $("#" + 'DialogProfile').modal('hide');
                                gridProfileOptions.bootgrid("reload");
                            }, true);
                    });
                } else {
                    console.log("[grid] action add missing")
                }
            });

            // delete single profile at a go
            $(this).find(".command-delete").on("click", function (e) {
                if (gridProfileParams['del'] !== undefined) {
                    var uuid = $(this).data("row-id");
                    let profile = $(this).data("row-name");
                    // if (count !=="none"){
                    stdDialogConfirm('{{ lang._('
                    Confirm
                    Subcriber
                    Removal
                    ') }}', '{{ lang._('
                    Do
                    you
                    want
                    to
                    delete Profile
                    ') }}' + '{{ lang._('
                    ""
                    ')}}' + profile + '{{ lang._('
                    ""
                    ')}}' + '{{ lang._(' ? ')}}', '{{ lang._('
                    Yes
                    ') }}', '{{ lang._('
                    Cancel
                    ') }}', function () {
                        ajaxCall(url = '/api/opncell/profile/deleteProfile/' + uuid, sendData = {}, callback = function (data, status) {
                            updateServiceControlUI('opncell');
                            gridProfileOptions.bootgrid('reload');
                        });
                    }
                )
                    // }  else {
                    //
                    //     }
                } else {
                    console.log("[grid] action del missing")
                }
            });

            // edit Profile

            $(this).find(".command-edit").on("click", function (e) {
                // edit dialog id to use

                const gridId = $(this).attr('id');

                if (gridProfileParams['get'] !== undefined) {
                    let uuid = $(this).data("row-id");
                    var count = $(this).data("row-count");
                    let urlMap = {};
                    urlMap['frm_' + 'DialogProfile'] = gridProfileParams['get'] + uuid;   //pass the uuid of the row of interest
                    mapDataToFormUI(urlMap).done(function () {
                        // update selectors
                        formatTokenizersUI();
                        $('.selectpicker').selectpicker('refresh');
                        // clear validation errors (if any)
                        clearFormValidation('frm_' + 'DialogProfile');
                    });
                    updateServiceControlUI('opncell')
                    // show dialog for pipe edit
                    $('#' + 'DialogProfile').modal({backdrop: 'static', keyboard: false});
                    // define save action
                    $("#btn_" + 'DialogProfile' + "_save").unbind('click').click(function () {
                        console.log("clicked")
                        if (gridProfileParams['set'] !== undefined) {
                            saveFormToEndpoint(url = gridProfileParams['set'] + uuid,
                                formid = 'frm_' + 'DialogProfile', callback_ok = function (data,status) {
                                    console.log(data)
                                    $("#" + 'DialogProfile').modal('hide');
                                    gridProfileOptions.bootgrid('reload');
                                    // std_bootgrid_reload(gridId);
                                }, true);
                        } else {
                            console.log("[grid] action set missing")
                        }
                    });
                } else {
                    console.log("[grid] action get or data-editDialog missing")
                }
            });

        });

    });

    /**
     *  Hnet stuff
     * **/
    $(document).ready(function () {
        const networkLabels = {
            enablefour: "4G",
            enablefiveSA: "5G SA",
            enablefiveNSA: "5G NSA",
            enableupf: "UPF"
        };

        mapDataToFormUI({'frm_hnet_settings': "/api/opncell/hnet/get"}).done(function (data) {
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
        });

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
                        updateServiceControlUI("opncell");
                        dialogRef.close();
                    });
                }
            });
        }

        $("#hnetResultModal").on("hidden.bs.modal", function () {
            const network = localStorage.getItem("networkName");

            if (network !== "enablefiveSA") {
                BootstrapDialog.confirm({
                    title: 'Confirm Network Change',
                    message: 'Keys successfully generated! Do you want to activate 5G SA network?',
                    type: BootstrapDialog.TYPE_WARNING,
                    btnOKLabel: 'Proceed',
                    btnCancelLabel: 'No',
                    callback: function (result) {
                        if (result) {
                            localStorage.setItem('networkName', 'enablefiveSA');
                            activateNetwork('enablefiveSA');
                        }
                    }
                });
            }
        });

        $("#generateAct_hnet").off('click').on('click', function () {
            BootstrapDialog.confirm({
                title: 'Generate a new key for SUCI concealment!',
                message: 'This mints a brand new key pair and adds it as a new Hnet ID. Existing keys already provisioned to USIMs will keep working. Proceed?',
                type: BootstrapDialog.TYPE_WARNING,
                btnOKLabel: 'Proceed',
                btnCancelLabel: 'No',
                callback: function (result) {
                    if (!result) {
                        return;
                    }

                    $("#generateAct_hnet_progress").addClass("fa fa-spinner fa-pulse");
                    $("#generateAct_hnet").prop("disabled", true);

                    ajaxCall('/api/opncell/hnet/generate', {}, function (data, status) {
                        $("#generateAct_hnet_progress").removeClass("fa fa-spinner fa-pulse");
                        $("#generateAct_hnet").prop("disabled", false);

                        if (data.data === null) {
                            const msg = 'Try checking if `configd` is running. If not run `service configd start`';
                            BootstrapDialog.show({
                                message: "{{ lang._('Key generation failed! ') }}" + msg,
                                type: BootstrapDialog.TYPE_DANGER,
                                title: "{{ lang._('Error! Something went wrong.') }}",
                                closable: true
                            });
                            return;
                        }

                        let payload = data.data;
                        if (typeof payload === "string") {
                            payload = JSON.parse(payload);
                        }

                        // fill result modal
                        if (payload.result === "ok") {
                            $("#hnet_result_path").text(payload.public_key_path);
                            $("#hnet_result_priv_path").text(payload.private_key_path);
                            $("#hnet_result_hex").text(payload.public_key_hex);
                            $("#hnet_result_pem").text(payload.public_key_pem);
                            $("#hnet_id").text(payload.id);
                            $("#hnetResultModal").modal("show");
                        } else {
                            BootstrapDialog.show({
                                message: "{{ lang._('Key generation failed with error  ') }}" + payload.error,
                                type: BootstrapDialog.TYPE_DANGER,
                                title: "{{ lang._('Error! Something went wrong.') }}",
                                closable: true
                            });
                        }
                    });
                }
            });
        });

        $("#existing_keys").off('click').on("click", function () {
            $("#activate_progress").addClass("fa fa-spinner fa-pulse");

            ajaxCall('/api/opncell/hnet/list', {}, function (data, status) {
                $("#activate_progress").removeClass("fa fa-spinner fa-pulse");

                let payload = data.data;
                if (typeof payload === "string") {
                    payload = JSON.parse(payload);
                }

                const entries = (payload && payload.entries) || [];
                const $body = $("#hnet_list_body");
                $body.empty();

                if (entries.length === 0) {
                    $body.append('<tr><td colspan="4">{{ lang._("No Hnet keys have been generated yet.") }}</td></tr>');
                }

                entries.forEach(function (entry) {
                    const schemeLabel = entry.scheme === 1 ? 'Profile A (curve25519)' : 'Profile B (secp256r1)';
                    const $row = $('<tr></tr>');
                    $row.append($('<td></td>').text(entry.id));
                    $row.append($('<td></td>').text(schemeLabel));
                    $row.append($('<td style="word-break: break-all;"></td>').text(entry.private_key_path || ''));

                    const $pubCell = $('<td></td>');
                    if (entry.error) {
                        $pubCell.text(entry.error);
                    } else {
                        const $hexBtn = $('<button type="button" class="btn btn-xs btn-default">{{ lang._("Copy HEX") }}</button>');
                        $hexBtn.on('click', function () {
                            navigator.clipboard.writeText(entry.public_key_hex).then(() => {
                                $hexBtn.text('{{ lang._("Copied!") }}');
                                setTimeout(() => $hexBtn.text('{{ lang._("Copy HEX") }}'), 1500);
                            });
                        });
                        const $pemBtn = $('<button type="button" class="btn btn-xs btn-default __ml">{{ lang._("Copy PEM") }}</button>');
                        $pemBtn.on('click', function () {
                            navigator.clipboard.writeText(entry.public_key_pem).then(() => {
                                $pemBtn.text('{{ lang._("Copied!") }}');
                                setTimeout(() => $pemBtn.text('{{ lang._("Copy PEM") }}'), 1500);
                            });
                        });
                        $pubCell.append($hexBtn).append($pemBtn);
                    }
                    $row.append($pubCell);
                    $body.append($row);
                });

                $("#hnetListModal").modal("show");
            });
        });

        $("#activate_existing_hnet").off('click').on('click', function () {
            const network = localStorage.getItem("networkName");
            let message;
            if (network === "enablefiveSA") {
                message = 'Re-loading the network! This will restart all services. Proceed?';
            } else if (networkLabels[network]) {
                message = 'The ' + networkLabels[network] + ' network is currently active! Do you want to switch to 5G SA?';
            } else {
                message = 'Do you want to activate the 5G SA network?';
            }

            BootstrapDialog.confirm({
                title: 'Confirm Network Change',
                message: message,
                type: BootstrapDialog.TYPE_WARNING,
                btnOKLabel: 'Proceed',
                btnCancelLabel: 'No',
                callback: function (result) {
                    if (result) {
                        $("#hnetListModal").modal("hide");
                        localStorage.setItem('networkName', 'enablefiveSA');
                        activateNetwork('enablefiveSA');
                    }
                }
            });
        });

        $("#copy_hex_btn").on("click", function () {
            const text = $("#hnet_result_hex").text();
            navigator.clipboard.writeText(text).then(() => {
                $(this).text("Copied!");
                setTimeout(() => $(this).html('<i class="fa fa-copy"></i> Copy HEX'), 1500);
            });
        });

        $("#copy_pem_btn").on("click", function () {
            const text = $("#hnet_result_pem").text();
            navigator.clipboard.writeText(text).then(() => {
                $(this).text("Copied!");
                setTimeout(() => $(this).html('<i class="fa fa-copy"></i> Copy PEM'), 1500);
            });
        });
    });

</script>
{# include dialogs #}
{{ partial("layout_partials/base_dialog",['fields':formDialogEditUser,'id':'DialogUsers','label':lang._('Change user Profile:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog",['fields':formDialogAddUser,'id':'DialogAddUsers','label':lang._('Add Subscriber:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog",['fields':formDialogEditProfile,'id':'DialogProfile','label':lang._('Edit Profile Details:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog_processing") }}
