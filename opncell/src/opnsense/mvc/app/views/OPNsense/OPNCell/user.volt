{#

Copyright (C) 2023 Digital Solutions
Copyright (C) 2023 Wire lab
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
                {{ lang._('An Error occurred. Check if the db is up and running, then try again.') }}<br>
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
                    <button data-action="add" type="button" class="btn btn-xs btn-default"><span
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
                    <button data-action="add" type="button" class="btn btn-xs btn-default"><span
                            class="fa fa-plus"></span></button>
                </td>
            </tr>
            </tfoot>
        </table>

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
        }, 3000);

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
        };

        let gridOptions = $("#grid-user-list").UIBootgrid({
            ajax: true,
            selection: true,
            multiSelect: true,
            rowCount: [10, 25, 50, 100, 500, 1000],
            search: '/api/opncell/user/searchSub',
            get: '/api/opncell/user/getSub/',
            set: '/api/opncell/user/setSub/',
            add: '/api/opncell/user/addSub/',
            del: '/api/opncell/user/deleteSub/',
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
         * copy actions for selected items from opnsense_bootgrid_plugin.js
         */
        gridOptions.on("loaded.rs.jquery.bootgrid", function (e) {

            $(this).find("*[data-action=add]").off('click');
            $(this).find(".command-edit").off('click');
            $(this).find(".command-delete").off('click');
            $(this).find("*[data-action=deleteSelected]").off('click')

            // add a new user
            $(this).find("*[data-action=add]").on('click' ,function () {
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
                                $("#" + 'DialogAddUsers').modal('hide');
                               gridOptions.bootgrid("reload");
                                if (data.result === "failed") {
                                    $("#failedSave").attr("style", "display:block");
                                    fadeOut("#failedSave")
                                } else if(data.result === "saved"  || data.result === "Success" ) {
                                    $("#successfulSave").attr("style", "display:block");
                                    fadeOut("#successfulSave")
                                } else {
                                    $("#Error").attr("style", "display:block");
                                    fadeOut("#Error")
                                }
                            }, true);
                    });
                } else {
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
                                    // updateServiceControlUI('opncore');
                                    // grid_users.bootgrid('reload');
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
        // gridOptions.on("loaded.rs.jquery.bootgrid", function (e) {
        //     // toggle all rendered tooltips (once for all)
        //     $('.bootgrid-tooltip').tooltip();
        //
        //     // scale footer on resize
        //     $(this).find("tfoot td:first-child").attr('colspan', $(this).find("th").length - 1);
        //     $(this).find('tr[data-row-id]').each(function () {
        //         if ($(this).find('[class*="command-toggle"]').first().data("value") === "0") {
        //             $(this).addClass("text-muted");
        //         }
        //     });
        //
        //     // edit dialog id to use
        //     let gridId = $(this).attr('id');
        //     console.log(gridId)
        //
        //     // delete  multiple users at once
        //     $(this).find("*[data-action=deleteSelected]").click(function () {
        //
        //         console.log("clicked");
        //         if (gridParams['del'] !== undefined) {
        //             stdDialogConfirm('{{ lang._("Confirm User removal") }}', '{{ lang._("Do you want to remove the selected users ? ") }}', '{{ lang._("Yes") }}', '{{ lang._("Cancel") }}', function () {
        //                     var rows = $("#" + gridId).bootgrid('getSelectedRows');
        //                     console.log(rows);
        //                     if (rows !== undefined) {
        //                         let imsi = $(this).data("row-imsi");
        //                         let uuid = $(this).data("row-uuid");
        //                         var deferreds = [];
        //                         $.each(rows, function (key, uuid) {
        //                             deferreds.push(ajaxCall(url = '/api/opncell/user/deleteSub/' + uuid, sendData = {}, null));
        //                         });
        //                         // refresh after load
        //                         $.when.apply(null, deferreds).done(function () {
        //                             std_bootgrid_reload(gridId);
        //                             // updateServiceControlUI('opncore');
        //                             // grid_users.bootgrid('reload');
        //                         });
        //                     } else {
        //                         console.log("undefined")
        //                     }
        //                 }
        //             )
        //
        //         } else {
        //             console.log("[grid] action del missing")
        //         }
        //     });
        // });

        // Manually doing the table for subscribers--For customization ---Profile Edition
        let gridProfileParams = {
                search: '/api/opncell/profile/searchProfile',
                get: '/api/opncell/profile/editProfile/',
                set: '/api/opncell/profile/setProfile/',
                add: '/api/opncell/profile/addProfile/',
                del: '/api/opncell/profile/deleteProfile/',
            };

        let gridProfileOptions = $("#grid-profile-list").UIBootgrid({
            search: '/api/opncell/profile/searchProfile',
            get: '/api/opncell/profile/editProfile/',
            set: '/api/opncell/profile/setProfile/',
            add: '/api/opncell/profile/addProfile/',
            del: '/api/opncell/profile/deleteProfile/',
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

            // link Add new to child button with data-action = add
            $(this).find("*[data-action=add]").click(function () {
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
            const editDlg = $(this).attr('data-editDialog');
            $(this).find(".command-edit").on("click", function (e) {
                // edit dialog id to use
                console.log(editDlg)
                const gridId = $(this).attr('id');

                if (editDlg !== undefined && gridProfileParams['get'] !== undefined) {
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

</script>
{# include dialogs #}
{{ partial("layout_partials/base_dialog",['fields':formDialogEditUser,'id':'DialogUsers','label':lang._('Change user Profile:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog",['fields':formDialogAddUser,'id':'DialogAddUsers','label':lang._('Add Subscriber:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog",['fields':formDialogEditProfile,'id':'DialogProfile','label':lang._('Edit Profile Details:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog_processing") }}