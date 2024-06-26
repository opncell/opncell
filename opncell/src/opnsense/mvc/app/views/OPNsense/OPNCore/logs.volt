{#
# Copyright (c) 2022 Robbert Rijkse
# Copyright (c) 2019 Deciso B.V.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
# 2.  Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#}

<script>
    $( document ).ready(function() {
        // get entries from named/named.log
        let grid_mmelog = $("#grid-mmelog").UIBootgrid({
            options:{
                sorting:false,
                rowSelect: false,
                selection: false,
                rowCount:[20,50,100,200,500,1000,-1],
            },
            search:'/api/diagnostics/log/opncore/mme'
        });

        // get entries from named/query.log
        let grid_querylog = $("#grid-querylog").UIBootgrid({
            options:{
                sorting:false,
                rowSelect: false,
                selection: false,
                rowCount:[20,50,100,200,500,1000,-1],
            },
            search:'/api/diagnostics/log/named/named'
        });

        // get entries from named/rpz.log
        let grid_blockedlog = $("#grid-blockedlog").UIBootgrid({
            options:{
                sorting:false,
                rowSelect: false,
                selection: false,
                rowCount:[20,50,100,200,500,1000,-1],
            },
            search:'/api/diagnostics/log/named/rpz'
        });

        let grid_smflog = $("#grid-smflog").UIBootgrid({
            options:{
                sorting:false,
                rowSelect: false,
                selection: false,
                rowCount:[20,50,100,200,500,1000,-1],
            },
            search:'/api/diagnostics/log/opncore/smf'
        });

        let grid_sgwclog = $("#grid-sgwclog").UIBootgrid({
            options:{
                sorting:false,
                rowSelect: false,
                selection: false,
                rowCount:[20,50,100,200,500,1000,-1],
            },
            search:'/api/diagnostics/log/opncore/sgwc'
        });

        let grid_sgwulog = $("#grid-sgwulog").UIBootgrid({
            options:{
                sorting:false,
                rowSelect: false,
                selection: false,
                rowCount:[20,50,100,200,500,1000,-1],
            },
            search:'/api/diagnostics/log/opncore/sgwu'
        });

        grid_mmelog.on("loaded.rs.jquery.bootgrid", function(){
            $(".action-page").click(function(event){
                event.preventDefault();
                $("#grid-mmelog").bootgrid("search",  "");
                let new_page = parseInt((parseInt($(this).data('row-id')) / $("#grid-log").bootgrid("getRowCount")))+1;
                $("input.search-field").val("");
                // XXX: a bit ugly, but clearing the filter triggers a load event.
                setTimeout(function(){
                    $("ul.pagination > li:last > a").data('page', new_page).click();
                }, 100);
            });
        });

        grid_querylog.on("loaded.rs.jquery.bootgrid", function(){
            $(".action-page").click(function(event){
                event.preventDefault();
                $("#grid-querylog").bootgrid("search",  "");
                let new_page = parseInt((parseInt($(this).data('row-id')) / $("#grid-log").bootgrid("getRowCount")))+1;
                $("input.search-field").val("");
                // XXX: a bit ugly, but clearing the filter triggers a load event.
                setTimeout(function(){
                    $("ul.pagination > li:last > a").data('page', new_page).click();
                }, 100);
            });
        });

        grid_blockedlog.on("loaded.rs.jquery.bootgrid", function(){
            $(".action-page").click(function(event){
                event.preventDefault();
                $("#grid-blockedlog").bootgrid("search",  "");
                let new_page = parseInt((parseInt($(this).data('row-id')) / $("#grid-log").bootgrid("getRowCount")))+1;
                $("input.search-field").val("");
                // XXX: a bit ugly, but clearing the filter triggers a load event.
                setTimeout(function(){
                    $("ul.pagination > li:last > a").data('page', new_page).click();
                }, 100);
            });
        });

        grid_smflog.on("loaded.rs.jquery.bootgrid", function(){
            $(".action-page").click(function(event){
                event.preventDefault();
                $("#grid-smflog").bootgrid("search",  "");
                let new_page = parseInt((parseInt($(this).data('row-id')) / $("#grid-log").bootgrid("getRowCount")))+1;
                $("input.search-field").val("");
                // XXX: a bit ugly, but clearing the filter triggers a load event.
                setTimeout(function(){
                    $("ul.pagination > li:last > a").data('page', new_page).click();
                }, 100);
            });
        });

        grid_sgwclog.on("loaded.rs.jquery.bootgrid", function(){
            $(".action-page").click(function(event){
                event.preventDefault();
                $("#grid-sgwclog").bootgrid("search",  "");
                let new_page = parseInt((parseInt($(this).data('row-id')) / $("#grid-log").bootgrid("getRowCount")))+1;
                $("input.search-field").val("");
                // XXX: a bit ugly, but clearing the filter triggers a load event.
                setTimeout(function(){
                    $("ul.pagination > li:last > a").data('page', new_page).click();
                }, 100);
            });
        });

        grid_sgwulog.on("loaded.rs.jquery.bootgrid", function(){
            $(".action-page").click(function(event){
                event.preventDefault();
                $("#grid-sgwulog").bootgrid("search",  "");
                let new_page = parseInt((parseInt($(this).data('row-id')) / $("#grid-log").bootgrid("getRowCount")))+1;
                $("input.search-field").val("");
                // XXX: a bit ugly, but clearing the filter triggers a load event.
                setTimeout(function(){
                    $("ul.pagination > li:last > a").data('page', new_page).click();
                }, 100);
            });
        });

    });
</script>


<ul class="nav nav-tabs" role="tablist" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#mmelog"><b>{{ lang._('MME') }}</b></a></li>
    <li><a data-toggle="tab" href="#amflog">{{ lang._('AMF') }}</a></li>
    <li><a data-toggle="tab" href="#upflog">{{ lang._('UPF') }}</a></li>
    <li><a data-toggle="tab" href="#smflog">{{ lang._('SMF') }}</a></li>
    <li><a data-toggle="tab" href="#sgwclog">{{ lang._('SGWC') }}</a></li>
</ul>

<div class="content-box tab-content">

    <div id="mmelog" class="tab-pane fade in active">
        <div class="content-box" style="padding-bottom: 1.5em;">
            <div  class="col-sm-12">
                <table id="grid-mmelog" class="table table-condensed table-hover table-striped table-responsive" data-store-selection="true">
                    <thead>
                    <tr>
                        <th data-column-id="timestamp" data-width="15em" data-type="string">{{ lang._('Date') }}</th>
                        <th data-column-id="process_name" data-width="9em" data-type="string">{{ lang._('Type') }}</th>
                        <th data-column-id="severity" data-width="11em" data-type="string">{{ lang._('Level')}}</th>
                        <th data-column-id="line" data-type="string">{{ lang._('Line') }}</th>
                    </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div id="amflog" class="tab-pane fade">
        <div class="content-box" style="padding-bottom: 1.5em;">
            <div  class="col-sm-12">
                <table id="grid-querylog" class="table table-condensed table-hover table-striped table-responsive" data-store-selection="true">
                    <thead>
                    <tr>
                        <th data-column-id="timestamp" data-width="15em" data-type="string">{{ lang._('Date') }}</th>
                        <th data-column-id="process_name" data-width="9em" data-type="string">{{ lang._('Type') }}</th>
                        <th data-column-id="severity" data-width="11em" data-type="string">{{ lang._('Level')}}</th>
                        <th data-column-id="line" data-type="string">{{ lang._('Line') }}</th>
                    </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div id="smflog" class="tab-pane fade">
        <div class="content-box" style="padding-bottom: 1.5em;">
            <div  class="col-sm-12">
                <table id="grid-smflog" class="table table-condensed table-hover table-striped table-responsive" data-store-selection="true">
                    <thead>
                    <tr>
                        <th data-column-id="timestamp" data-width="15em" data-type="string">{{ lang._('Date') }}</th>
                        <th data-column-id="process_name" data-width="9em" data-type="string">{{ lang._('Type') }}</th>
                        <th data-column-id="severity" data-width="11em" data-type="string">{{ lang._('Level')}}</th>
                        <th data-column-id="line" data-type="string">{{ lang._('Line') }}</th>
                    </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div id="sgwclog" class="tab-pane fade">
        <div class="content-box" style="padding-bottom: 1.5em;">
            <div  class="col-sm-12">
                <table id="grid-sgwclog" class="table table-condensed table-hover table-striped table-responsive" data-store-selection="true">
                    <thead>
                    <tr>
                        <th data-column-id="timestamp" data-width="15em" data-type="string">{{ lang._('Date') }}</th>
                        <th data-column-id="process_name" data-width="9em" data-type="string">{{ lang._('Type') }}</th>
                        <th data-column-id="severity" data-width="11em" data-type="string">{{ lang._('Level')}}</th>
                        <th data-column-id="line" data-type="string">{{ lang._('Line') }}</th>
                    </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div id="sgwulog" class="tab-pane fade">
        <div class="content-box" style="padding-bottom: 1.5em;">
            <div  class="col-sm-12">
                <table id="grid-sgwulog" class="table table-condensed table-hover table-striped table-responsive" data-store-selection="true">
                    <thead>
                    <tr>
                        <th data-column-id="timestamp" data-width="15em" data-type="string">{{ lang._('Date') }}</th>
                        <th data-column-id="process_name" data-width="9em" data-type="string">{{ lang._('Type') }}</th>
                        <th data-column-id="severity" data-width="11em" data-type="string">{{ lang._('Level')}}</th>
                        <th data-column-id="line" data-type="string">{{ lang._('Line') }}</th>
                    </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div id="upflog" class="tab-pane fade">
        <div class="content-box" style="padding-bottom: 1.5em;">
            <div  class="col-sm-12">
                <table id="grid-blockedlog" class="table table-condensed table-hover table-striped table-responsive" data-store-selection="true">
                    <thead>
                    <tr>
                        <th data-column-id="timestamp" data-width="15em" data-type="string">{{ lang._('Date') }}</th>
                        <th data-column-id="process_name" data-width="9em" data-type="string">{{ lang._('Type') }}</th>
                        <th data-column-id="severity" data-width="11em" data-type="string">{{ lang._('Level')}}</th>
                        <th data-column-id="line" data-type="string">{{ lang._('Line') }}</th>
                    </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

</div>
