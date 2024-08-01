

<tr id="row_<?= $id ?>" <?php if ((empty($advanced) ? (false) : ($advanced)) == 'true') { ?> data-advanced="true"<?php } ?>>
    <td>
        <div class="control-label" id="control_label_<?= $id ?>">
            <?php if ((empty($help) ? (false) : ($help))) { ?>
                <a id="help_for_<?= $id ?>" href="#" class="showhelp"><i class="fa fa-info-circle"></i></a>
            <?php } elseif ((empty($help) ? (false) : ($help)) == false) { ?>
                <i class="fa fa-info-circle text-muted"></i>
            <?php } ?>
            <b><?= $label ?></b>
        </div>
    </td>
    <td>
        <?php if ($type == 'text') { ?>
            <input  type="text" aria-label="<?= view_html_safe($label) ?>"
                    class="form-control <?= (empty($style) ? ('') : ($style)) ?>"
                    size="<?= (empty($size) ? ('50') : ($size)) ?>"
                    id="<?= $id ?>"
                    <?= ((empty($readonly) ? (false) : ($readonly)) ? 'readonly="readonly"' : '') ?>
                    <?php if ((empty($hint) ? (false) : ($hint))) { ?>placeholder="<?= $hint ?>"<?php } ?>
            >
        <?php } elseif ($type == 'hidden') { ?>
            <input type="hidden" id="<?= $id ?>" class="<?= (empty($style) ? ('') : ($style)) ?>" >
        <?php } elseif ($type == 'checkbox') { ?>
            <input type="checkbox"  class="<?= (empty($style) ? ('') : ($style)) ?>" id="<?= $id ?>" aria-label="<?= view_html_safe($label) ?>">
        <?php } elseif ($this->isIncluded($type, ['select_multiple', 'dropdown'])) { ?>
            <div id="select_<?= $id ?>">
            <select aria-label="<?= view_html_safe($label) ?>" <?php if ($type == 'select_multiple') { ?>multiple="multiple"<?php } ?>
                    data-size="<?= (empty($size) ? (10) : ($size)) ?>"
                    id="<?= $id ?>"
                    class="<?= (empty($style) ? ('selectpicker') : ($style)) ?>"
                    data-container="body"
                    <?php if ((empty($hint) ? (false) : ($hint))) { ?>data-hint="<?= $hint ?>"<?php } ?>
                    data-width="<?= (empty($width) ? ('346px') : ($width)) ?>"
                    data-allownew="<?= (empty($allownew) ? ('false') : ($allownew)) ?>"
                    data-sortable="<?= (empty($sortable) ? ('false') : ($sortable)) ?>"
                    data-live-search="true"
                    <?php if ((empty($separator) ? (false) : ($separator))) { ?>data-separator="<?= $separator ?>"<?php } ?>
            ></select>
            <?php if ($type == 'select_multiple') { ?>
              <?php $this_style = explode(' ', $style ?? '');?>
              <?php if (!$this->isIncluded('tokenize', $this_style)) { ?><br /><?php } ?>
                <a href="#" class="text-danger" id="clear-options_<?= $id ?>"><i class="fa fa-times-circle"></i> <small><?= $lang->_('Clear All') ?></small></a>
              <?php if ($this->isIncluded('tokenize', $this_style)) { ?>&nbsp;&nbsp;<a href="#" class="text-danger" id="copy-options_<?= $id ?>"><i class="fa fa-copy"></i> <small><?= $lang->_('Copy') ?></small></a>
              &nbsp;&nbsp;<a href="#" class="text-danger" id="paste-options_<?= $id ?>" style="display:none"><i class="fa fa-paste"></i> <small><?= $lang->_('Paste') ?></small></a>
              <?php if ((empty($allownew) ? ('false') : ($allownew))) { ?>
              &nbsp;&nbsp;<a href="#" class="text-danger" id="to-text_<?= $id ?>" ><i class="fa fa-file-text-o"></i> <small><?= $lang->_('Text') ?></small> </a>
              <?php } ?>
              <?php } else { ?>
                &nbsp;
                <a href="#" class="text-danger" id="select-options_<?= $id ?>"><i class="fa fa-check-circle"></i> <small><?= $lang->_('Select All') ?></small></a>
              <?php } ?>
            <?php } ?>
            </div>
            <div id="textarea_<?= $id ?>" style="display: none;">
                <textarea>

                </textarea>
                <a href="#" class="text-danger" id="to-select_<?= $id ?>" ><i class="fa fa-th-list"></i> <small><?= $lang->_('Back') ?></small> </a>
            </div>
        <?php } elseif ($type == 'password') { ?>
            <input type="password" autocomplete="new-password" class="form-control <?= (empty($style) ? ('') : ($style)) ?>" size="<?= (empty($size) ? ('50') : ($size)) ?>" id="<?= $id ?>" <?= ((empty($readonly) ? (false) : ($readonly)) ? 'readonly="readonly"' : '') ?> aria-label="<?= view_html_safe($label) ?>">
        <?php } elseif ($type == 'textbox') { ?>
            <textarea class="<?= (empty($style) ? ('') : ($style)) ?>" rows="<?= (empty($height) ? ('5') : ($height)) ?>" id="<?= $id ?>" <?= ((empty($readonly) ? (false) : ($readonly)) ? 'readonly="readonly"' : '') ?> aria-label="<?= view_html_safe($label) ?>"></textarea>
        <?php } elseif ($type == 'info') { ?>
            <span  class="<?= (empty($style) ? ('') : ($style)) ?>" id="<?= $id ?>"></span>
        <?php } ?>
        <?php if ((empty($help) ? (false) : ($help))) { ?>
            <div class="hidden" data-for="help_for_<?= $id ?>">
                <small><?= $help ?></small>
            </div>
        <?php } ?>
    </td>
    <td>
        <span class="help-block" id="help_block_<?= $id ?>"></span>
    </td>
</tr>
