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
        <div id="no_file" class="alert alert-dismissible alert-info" style="display: none" role="alert">
            {{ lang._('No file detected. Kindly attach a file') }}<br>
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
            </div> <div id="successfulSave" class="alert alert-dismissible alert-info" style="display: none" role="alert">
                {{ lang._('Subscriber added') }}<br>
            </div>
        </div>
        <div class="col-md-12 __mt">
            <div  id="failedDelete" class="alert alert-dismissible alert-info" style="display: none" role="alert">
                {{ lang._('Subscriber not deleted') }}
            </div>
            <div id="successfulDelete" class="alert alert-dismissible alert-info" style="display: none" role="alert">
            {{ lang._('Subscriber deleted successfully') }}
            </div>
        </div>
        <button class="btn btn-danger" style="display: none; margin-left: 6px;text-align: center" id="deleting" type="button">
            <b>{{ lang._('Deleting....') }}</b> <i id="deleting_progress"></i>
        </button>

        <table id="grid-user-list" class="table table-condensed table-hover table-striped table-responsive"
               data-editDialog="DialogUsers" data-addDialog="DialogAddUsers">
            <thead>
            <tr>
                <th data-column-id="imsi" data-type="string" data-visible="true">{{ lang._('IMSI') }}</th>
                <th data-column-id="profile" data-type="string" data-visible="true">{{ lang._('Profile') }}</th>
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
                <td>
                    <button data-action="deleteSelected" type="button" class="btn btn-xs btn-default"><span
                            class="fa fa-trash-o"></span></button>
                </td>
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
                <th data-column-id="apn" data-type="string" data-visible="true">{{ lang._('Name') }}</th>
                <th data-column-id="count" data-type="string" data-visible="true">{{ lang._('Subscribed users') }}</th>
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
        saveFormToEndpoint(url = "/api/opncore/user/addSub", formid = 'frm_user_settings', callback_ok = function (data, status) {
            $("#saveAct_users_progress").removeClass("fa fa-spinner fa-pulse");

        }, true);

    }

    function saveBulkUsers() {

        $("#saveBulkAct_users_progress").addClass("fa fa-spinner fa-pulse");

        saveFormToEndpoint(url = "/api/opncore/bulk/addBulkSub", formid = 'frm_bulk_settings', callback_ok = function (data) {
            console.log(data.uuid)
            ajaxCall(url = "/api/opncore/bulk/saveBulkUsers/" + data.uuid, sendData = {}, callback = function (data, status) {
                console.log(data)
               if(data.result === "Success"){
                   $("#saveBulkAct_users_progress").removeClass("fa fa-spinner fa-pulse");
                   $("#file_uploaded").attr("style", "display:none");
                   $("#no_file").attr("style", "display:none");

               }
            });

        }, true);

    }

    function saveProfile() {
        $("#saveAct_profile_progress").addClass("fa fa-spinner fa-pulse");
        saveFormToEndpoint(url = "/api/opncore/profile/addProfile", formid = 'frm_profile_settings', callback_ok = function () {
            $("#saveAct_profile_progress").removeClass("fa fa-spinner fa-pulse");
        }, true);

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
                    url: '/api/opncore/user/upload',
                    data: formData,
                    processData: false, // Don't process the data
                    contentType: false, // Don't set content type (let jQuery decide)
                    success: function (response) {
                        console.log('Response from server:', response);
                        if(response.result === 'failed'){

                            $("#no_file").attr("style", "display:block");
                            $("#saveAct_upload_progress").removeClass("fa fa-spinner fa-pulse");
                        } else {
                            globalFileContent = response;
                            $("#no_file").attr("style", "display:none");
                            $("#file_uploaded").attr("style", "display:block");
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

        let data_get_map = {'formDialogAddUser': "/api/opncore/user/getSub"};
        let data_get_map2 = {'frm_profile_settings': "/api/opncore/profile/getProfile"};
        let data_get_map3 = {'frm_bulk_settings': "/api/opncore/bulk/get"};

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
        updateServiceControlUI('opncore')

        // Automatically load the subscribers in the table
        $('#userList').on('click', function () {
            ajaxCall(url = "/api/opncore/user/searchSub", sendData = {}, callback = function (data, status) {
                $("#grid-user-list").bootgrid('reload');
            });

        });
        // Automatically load the subscribers in the table
        $('#ProfileList').on('click', function () {
            console.log("profile")
            ajaxCall(url = "/api/opncore/profile/searchProfile", sendData = {}, callback = function (data, status) {
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
            search: '/api/opncore/user/searchSub',
            get: '/api/opncore/user/editSub/',
            set: '/api/opncore/user/setSub/',
            add: '/api/opncore/user/getSub/',
            del: '/api/opncore/user/deleteSub/',
        };

        let gridOptions = {
            ajax: true,
            selection: true,
            multiSelect: true,
            rowCount: [10, 25, 50, 100, 500, 1000],
            url: '/api/opncore/user/searchSub',
            formatters: {
                "commands": function (column, row) {
                    return "<button type=\"button\" title=\"{{ lang._('Edit Profile') }}\" class=\"btn btn-xs btn-default command-edit bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-imsi=\"" + row.imsi + "\"><span class=\"fa fa-pencil\"></span></button> " +
                        "<button type=\"button\" title=\"{{ lang._('Delete user') }}\" class=\"btn btn-xs btn-default command-delete bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-imsi=\"" + row.imsi + "\"><span class=\"fa fa-trash-o\"></span></button>";
                },
            },
        };

        /**
         * copy actions for selected items from opnsense_bootgrid_plugin.js
         */
        $("#grid-user-list").bootgrid(gridOptions).on("loaded.rs.jquery.bootgrid", function (e) {
            // edit dialog id to use
            let addForm = $(this).attr('data-addDialog');
            // toggle all rendered tooltips (once for all)
            $('.bootgrid-tooltip').tooltip();

            // scale footer on resize
            $(this).find("tfoot td:first-child").attr('colspan', $(this).find("th").length - 1);
            $(this).find('tr[data-row-id]').each(function () {
                if ($(this).find('[class*="command-toggle"]').first().data("value") === "0") {
                    $(this).addClass("text-muted");
                }
            });

            let editUserDlg = $(this).attr('data-addDialog');
            let gridUserId = $(this).attr('id');

            // add a new user
            $(this).find("*[data-action=add]").click(function () {
                if (gridParams['add'] !== undefined) {
                    var urlMap = {};
                    urlMap['frm_' + editUserDlg] = gridParams['add'];
                    mapDataToFormUI(urlMap).done(function () {
                        // update selectors
                        formatTokenizersUI();
                        $('.selectpicker').selectpicker('refresh');
                        // clear validation errors (if any)
                        clearFormValidation('frm_' + editUserDlg);
                    });

                    $('#' + editUserDlg).modal({backdrop: 'static', keyboard: false});
                    //
                    $("#btn_" + editUserDlg + "_save").unbind('click').click(function () {
                        saveFormToEndpoint(url = "/api/opncore/user/addSub",
                            formid = 'frm_' + editUserDlg, callback_ok = function (data) {
                                console.log(data.result)
                                $("#" + editUserDlg).modal('hide');
                                $("#" + gridUserId).bootgrid("reload");
                                if (data.result === "failed") {
                                    $("#failedSave").attr("style", "display:block");
                                } else if(data.result === "saved"){
                                    $("#successfulSave").attr("style", "display:block");
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
                        $("#deleting_progress").addClass("fa fa-spinner fa-pulse");
                        ajaxCall(url = "/api/opncore/user/deleteSub/"  + uuid, sendData = {}, callback = function (data, status) {
                            if (data.result === "failed"){
                                $("#deleting").attr("style", "display:none");
                                $("#failedDelete").attr("style", "display:block");

                            } else {
                                $("#deleting").attr("style", "display:none");
                                 $("#successfulDelete").attr("style", "display:block");
                            }
                            console.log(data.result)
                            updateServiceControlUI('opncore');
                            $("#grid-user-list").bootgrid('reload');
                        });
                    }
                )
                } else {
                    console.log("[grid] action del missing")
                }
            });

            //Attach/replace/change a profile to existing user
            const editDlg = $(this).attr('data-editDialog');
            const gridId = $(this).attr('id');
            $(this).find(".command-edit").on("click", function (e) {
                // edit dialog id to use
                if (editDlg !== undefined && gridParams['get'] !== undefined) {
                    let imsi = $(this).data("row-imsi");
                    let uuid = $(this).data("row-id");
                    let urlMap = {};

                    // urlMap['frm_' + editDlg] = '/api/opncore/user/getSingleSub/' + imsi;   //pass the imsi of the row of interest
                    urlMap['frm_' + editDlg] = gridParams['get'] + uuid;
                    mapDataToFormUI(urlMap).done(function () {
                        // update selectors
                        formatTokenizersUI();
                        $('.selectpicker').selectpicker('refresh');
                        // clear validation errors (if any)
                        clearFormValidation('frm_' + editDlg);
                    });
                    updateServiceControlUI('opncore')
                    // show dialog for pipe edit
                    $('#' + editDlg).modal({backdrop: 'static', keyboard: false});
                    // define save action
                    $("#btn_" + editDlg + "_save").unbind('click').click(function () {
                        $("#btn_" + editDlg + "_save").append('<i id="saveBulkAct_users_progress"></i>').addClass("fa fa-spinner")
                        if (gridParams['set'] !== undefined) {
                            saveFormToEndpoint(url = "/api/opncore/user/setSub/" + uuid, formid = 'frm_' + editDlg, callback_ok = function (data) {
                                $("#" + editDlg).modal('hide');
                                std_bootgrid_reload(gridId);
                                console.log(data)

                                // $("#saveAct_configs_progress").addClass("fa fa-spinner fa-pulse");
                                ajaxCall(url = "/api/opncore/user/reconfigureAct/" + network, sendData = {}, callback = function (data, status) {
                                    updateServiceControlUI('opncore');

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

        });

        /**
         * copy actions for selected items from opnsense_bootgrid_plugin.js
         */
        $("#grid-user-list").bootgrid(gridOptions).on("loaded.rs.jquery.bootgrid", function (e) {
            // toggle all rendered tooltips (once for all)
            $('.bootgrid-tooltip').tooltip();

            // scale footer on resize
            $(this).find("tfoot td:first-child").attr('colspan', $(this).find("th").length - 1);
            $(this).find('tr[data-row-id]').each(function () {
                if ($(this).find('[class*="command-toggle"]').first().data("value") === "0") {
                    $(this).addClass("text-muted");
                }
            });

            // edit dialog id to use
            let gridId = $(this).attr('id');
            console.log(gridId)

            // delete  multiple users at once
            $(this).find("*[data-action=deleteSelected]").click(function () {

                console.log("clicked");
                if (gridParams['del'] !== undefined) {
                    stdDialogConfirm('{{ lang._("Confirm User removal") }}', '{{ lang._("Do you want to remove the selected users ? ") }}', '{{ lang._("Yes") }}', '{{ lang._("Cancel") }}', function () {
                            var rows = $("#" + gridId).bootgrid('getSelectedRows');
                            console.log(rows);
                            if (rows !== undefined) {
                                let imsi = $(this).data("row-imsi");
                                let uuid = $(this).data("row-uuid");
                                var deferreds = [];
                                $.each(rows, function (key, uuid) {
                                    deferreds.push(ajaxCall(url = '/api/opncore/user/deleteSub/' + uuid, sendData = {}, null));
                                });
                                // refresh after load
                                $.when.apply(null, deferreds).done(function () {
                                    std_bootgrid_reload(gridId);
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

        // Manually doing the table for subscribers--For customization ---Profile Edition
        let gridProfileParams = {
            search: '/api/opncore/profile/searchProfile',
            get: '/api/opncore/profile/editProfile/',
            set: '/api/opncore/profile/setProfile/',
            add: '/api/opncore/profile/addProfile/',
            del: '/api/opncore/profile/deleteProfile/',
        };

        let gridProfileOptions = {
            ajax: true,
            selection: true,
            multiSelect: true,
            rowCount: [10, 25, 50, 100, 500, 1000],
            url: '/api/opncore/profile/searchProfile',
            formatters: {
                "commands": function (column, row) {
                    return "<button type=\"button\" title=\"{{ lang._('Edit profile') }}\" class=\"btn btn-xs btn-default command-edit bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-count=\"" + row.count + "\" data-row-imsi=\"" + row.imsi + "\"><span class=\"fa fa-pencil\"></span></button> " +
                        "<button type=\"button\" title=\"{{ lang._('Delete Profile') }}\" class=\"btn btn-xs btn-default command-delete bootgrid-tooltip\" data-row-id=\"" + row.uuid + "\" data-row-count=\"" + row.count + "\" data-row-name=\"" + row.apn + "\"><span class=\"fa fa-trash-o\"></span></button>";
                },
            },
        };

        /**
         * copy actions for selected items from opnsense_bootgrid_plugin.js
         */
        // edit profile dialog
        $("#grid-profile-list").bootgrid(gridProfileOptions).on("loaded.rs.jquery.bootgrid", function (e) {

            // toggle all rendered tooltips (once for all)
            $('.bootgrid-tooltip').tooltip();

            // scale footer on resize
            $(this).find("tfoot td:first-child").attr('colspan', $(this).find("th").length - 1);
            $(this).find('tr[data-row-id]').each(function () {
                if ($(this).find('[class*="command-toggle"]').first().data("value") == "0") {
                    $(this).addClass("text-muted");
                }
            });


            // edit profile dialog id to use
            var editProfileDlg = $(this).attr('data-editDialog');
            var gridId = $(this).attr('id');

            // link Add new to child button with data-action = add
            $(this).find("*[data-action=add]").click(function () {
                if (gridProfileParams['get'] !== undefined && gridProfileParams['add'] !== undefined) {
                    var urlMap = {};
                    urlMap['frm_' + editProfileDlg] = gridProfileParams['get'];
                    mapDataToFormUI(urlMap).done(function () {
                        // update selectors
                        formatTokenizersUI();
                        $('.selectpicker').selectpicker('refresh');
                        // clear validation errors (if any)
                        clearFormValidation('frm_' + editProfileDlg);
                    });

                    $('#' + editProfileDlg).modal({backdrop: 'static', keyboard: false});
                    //
                    $("#btn_" + editProfileDlg + "_save").unbind('click').click(function () {
                        saveFormToEndpoint(url = gridProfileParams['add'],
                            formid = 'frm_' + editProfileDlg, callback_ok = function () {
                                $("#" + editProfileDlg).modal('hide');
                                $("#" + gridId).bootgrid("reload");
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
                        ajaxCall(url = '/api/opncore/profile/deleteProfile/' + uuid, sendData = {}, callback = function (data, status) {
                            updateServiceControlUI('opncore');
                            $("#grid-profile-list").bootgrid('reload');
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
                    urlMap['frm_' + editDlg] = gridProfileParams['get'] + uuid;   //pass the uuid of the row of interest
                    mapDataToFormUI(urlMap).done(function () {
                        // update selectors
                        formatTokenizersUI();
                        $('.selectpicker').selectpicker('refresh');
                        // clear validation errors (if any)
                        clearFormValidation('frm_' + editDlg);
                    });
                    updateServiceControlUI('opncore')
                    // show dialog for pipe edit
                    $('#' + editDlg).modal({backdrop: 'static', keyboard: false});
                    // define save action
                    $("#btn_" + editDlg + "_save").unbind('click').click(function () {
                        console.log("clicked")
                        if (gridProfileParams['set'] !== undefined) {
                            saveFormToEndpoint(url = gridProfileParams['set'] + uuid,
                                formid = 'frm_' + editDlg, callback_ok = function (data,status) {
                                console.log(data)
                                    $("#" + editDlg).modal('hide');
                                    std_bootgrid_reload(gridId);
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

        /**
         * Delete multiple Profiles at once
         */
        $("#grid-profile-list").bootgrid(gridProfileOptions).on("loaded.rs.jquery.bootgrid", function (e) {
            // toggle all rendered tooltips (once for all)
            $('.bootgrid-tooltip').tooltip();

            // scale footer on resize
            $(this).find("tfoot td:first-child").attr('colspan', $(this).find("th").length - 1);
            $(this).find('tr[data-row-id]').each(function () {
                if ($(this).find('[class*="command-toggle"]').first().data("value") === "0") {
                    $(this).addClass("text-muted");
                }
            });

            // edit dialog id to use
            let gridId = $(this).attr('id');

            // link delete selected items action
            // $(this).find("*[data-action=deleteSelected]").click(function () {
            //     if (gridProfileParams['del'] !== undefined) {
            //         stdDialogConfirm('{{ lang._('
            //         Confirm
            //         User
            //         removal
            //         ') }}', '{{ lang._('
            //         Do
            //         you
            //         want
            //         to
            //         remove
            //         the
            //         selected
            //         users ? ') }}', '{{ lang._('
            //         Yes
            //         ') }}', '{{ lang._('
            //         Cancel
            //         ') }}', function () {
            //             var rows = $("#" + gridId).bootgrid('getSelectedRows');
            //             console.log(rows);
            //             if (rows !== undefined) {
            //                 let imsi = $(this).data("row-imsi");
            //                 let uuid = $(this).data("row-uuid");
            //                 var deferreds = [];
            //                 $.each(rows, function (key, uuid) {
            //                     deferreds.push(ajaxCall(url = '/api/opncore/user/deleteSub/' + uuid, sendData = {}, null));
            //                 });
            //                 // refresh after load
            //                 $.when.apply(null, deferreds).done(function () {
            //                     std_bootgrid_reload(gridId);
            //                     // updateServiceControlUI('opncore');
            //                     // grid_users.bootgrid('reload');
            //                 });
            //             } else {
            //                 console.log("undefined")
            //             }
            //         }
            //     )
            //
            //     } else {
            //         console.log("[grid] action del missing")
            //     }
            // });
        });


    });

</script>
{# include dialogs #}
{{ partial("layout_partials/base_dialog",['fields':formDialogEditUser,'id':'DialogUsers','label':lang._('Change user Profile:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog",['fields':formDialogAddUser,'id':'DialogAddUsers','label':lang._('Add Subscriber:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog",['fields':formDialogEditProfile,'id':'DialogProfile','label':lang._('Edit Profile Details:'),'hasSaveBtn':'true'])}}
{{ partial("layout_partials/base_dialog_processing") }}