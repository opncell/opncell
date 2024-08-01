




<?php $base_form_id = $id; ?>
<?php $help = false; ?>
<?php $advanced = false; ?>
<?php foreach ((empty($fields) ? ([]) : ($fields)) as $field) { ?>
<?php foreach ($field as $name => $element) { ?>
<?php if ($name == 'help') { ?>
<?php $help = true; ?>
<?php } ?>
<?php if ($name == 'advanced') { ?>
<?php $advanced = true; ?>
<?php } ?>
<?php } ?>
<?php if ((empty($help) ? (false) : ($help)) && (empty($advanced) ? (false) : ($advanced))) { ?>
<?php break; ?>
<?php } ?>
<?php } ?>
<form id="<?= $base_form_id ?>" class="form-inline" data-title="<?= (empty($data_title) ? ('') : ($data_title)) ?>">
  <div class="table-responsive">
    <table class="table table-striped table-condensed">
        <colgroup>
            <col class="col-md-3"/>
            <col class="col-md-4"/>
            <col class="col-md-5"/>
        </colgroup>
        <tbody>
<?php if ((empty($advanced) ? (false) : ($advanced)) || (empty($help) ? (false) : ($help))) { ?>
        <tr>
            <td style="text-align:left"><?php if ((empty($advanced) ? (false) : ($advanced))) { ?><a href="#"><i class="fa fa-toggle-off text-danger" id="show_advanced_<?= $base_form_id ?>"></i></a> <small><?= $lang->_('advanced mode') ?></small><?php } ?></td>
            <td colspan="2" style="text-align:right">
                <?php if ((empty($help) ? (false) : ($help))) { ?><small><?= $lang->_('full help') ?></small> <a href="#"><i class="fa fa-toggle-off text-danger" id="show_all_help_<?= $base_form_id ?>"></i></a><?php } ?>
            </td>
        </tr>
<?php } ?>
        <?php foreach ((empty($fields) ? ([]) : ($fields)) as $field) { ?>
            <?php if ($field['type'] == 'header') { ?>
              


      </tbody>
      <tfoot><tr><td colspan="3" style="padding: 0px;"></td></tr></tfoot>
    </table>
  </div>
  <div class="table-responsive <?= (empty($field['style']) ? ('') : ($field['style'])) ?>">
    <table class="table table-striped table-condensed table-responsive">
        <colgroup>
            <col class="col-md-3"/>
            <col class="col-md-4"/>
            <col class="col-md-5"/>
        </colgroup>
        <thead style="cursor: pointer;">
          <tr <?php if ((empty($field['advanced']) ? (false) : ($field['advanced'])) == 'true') { ?> data-advanced="true"<?php } ?>>
            <th colspan="3">
                <div style="padding-bottom: 5px; padding-top: 5px; font-size: 16px;">
                    <?php if ((empty($field['collapse']) ? (false) : ($field['collapse'])) == 'true') { ?>
                    <i class="fa fa-angle-right" aria-hidden="true"></i>
                    <?php } else { ?>
                    <i class="fa fa-angle-down" aria-hidden="true"></i>
                    <?php } ?>
                    &nbsp;
                    <b><?= $field['label'] ?></b>
                </div>
            </th>
          </tr>
        </thead>
        <tbody class="collapsible" <?php if ((empty($field['collapse']) ? (false) : ($field['collapse'])) == 'true') { ?>style="display: none;"<?php } ?>>


            <?php } else { ?>
              <?= $this->partial('layout_partials/form_input_tr', $field) ?>
            <?php } ?>
        <?php } ?>
        <?php if ((empty($apply_btn_id) ? ('') : ($apply_btn_id)) != '') { ?>
        <tr>
            <td colspan="3"><button class="btn btn-primary" id="<?= $apply_btn_id ?>" type="button"><b><?= $lang->_('Apply') ?></b> <i id="<?= $base_form_id ?>_progress" class=""></i></button></td>
        </tr>
        <?php } ?>
        </tbody>
        <tfoot><tr><td colspan="3" style="padding: 0px;"></td></tr></tfoot>
    </table>
  </div>
</form>
