// Home page "newest" / "cheapest" blocks: the tabs switch between
// pre-rendered product lists (one per root group, see build_group_sections).
//
// Lists are hidden with the `hidden` attribute on a wrapper, because the
// theme forces `.product-flexbox { display: flex !important }`, which beats
// any inline display:none.
(function ($) {
    // This file is included by both home blocks; run only once.
    if (window.__bazarakGroupTabs) { return; }
    window.__bazarakGroupTabs = true;

    // The same product can be present in several lists. Keep element ids
    // (e.g. favorite-btn-12) unique by leaving them only on the visible list,
    // so the like button updates the heart the visitor is actually looking at.
    function setIds(section, visible) {
        section.find('[id], [data-orig-id]').each(function () {
            var el = $(this);
            if (visible) {
                var original = el.attr('data-orig-id');
                if (original) {
                    el.attr('id', original).removeAttr('data-orig-id');
                }
            } else if (!el.attr('data-orig-id')) {
                el.attr('data-orig-id', el.attr('id')).removeAttr('id');
            }
        });
    }

    $(function () {
        $('.group-section[hidden]').each(function () {
            setIds($(this), false);
        });
    });

    $(document).on('click', '.block-header__group[data-group]', function () {
        var target = String($(this).data('group'));

        $(this).closest('.block-products-carousel')
            .find('.group-section')
            .each(function () {
                var section = $(this);
                var show = String(section.data('section')) === target;

                section.prop('hidden', !show);
                setIds(section, show);
            });
    });
})(jQuery);
