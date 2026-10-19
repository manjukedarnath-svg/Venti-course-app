/* @ds-bundle: {"format":4,"namespace":"SolsticeDesignSystem_a0f434","components":[{"name":"Button","sourcePath":"components/actions/Button.jsx"},{"name":"IconButton","sourcePath":"components/actions/IconButton.jsx"},{"name":"Badge","sourcePath":"components/display/Badge.jsx"},{"name":"Card","sourcePath":"components/display/Card.jsx"},{"name":"Icon","sourcePath":"components/display/Icon.jsx"},{"name":"ImageFrame","sourcePath":"components/display/ImageFrame.jsx"},{"name":"Tag","sourcePath":"components/display/Tag.jsx"},{"name":"Dialog","sourcePath":"components/feedback/Dialog.jsx"},{"name":"Toast","sourcePath":"components/feedback/Toast.jsx"},{"name":"Tooltip","sourcePath":"components/feedback/Tooltip.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Radio","sourcePath":"components/forms/Radio.jsx"},{"name":"Select","sourcePath":"components/forms/Select.jsx"},{"name":"Switch","sourcePath":"components/forms/Switch.jsx"},{"name":"Tabs","sourcePath":"components/navigation/Tabs.jsx"}],"sourceHashes":{"components/actions/Button.jsx":"e83759165df5","components/actions/IconButton.jsx":"e27848d4023e","components/display/Badge.jsx":"8757959c102b","components/display/Card.jsx":"a4288d054a08","components/display/Icon.jsx":"7a14c37c4dae","components/display/ImageFrame.jsx":"a8a0e98b197d","components/display/Tag.jsx":"8beb5bdab33f","components/feedback/Dialog.jsx":"67a381c93891","components/feedback/Toast.jsx":"015f6231027f","components/feedback/Tooltip.jsx":"691af27b2d87","components/forms/Checkbox.jsx":"4fae3de22581","components/forms/Input.jsx":"b5d192e3ae24","components/forms/Radio.jsx":"1dd36d305837","components/forms/Select.jsx":"766770d0628f","components/forms/Switch.jsx":"098d5bfa4841","components/navigation/Tabs.jsx":"45313145eab4","ui_kits/journal/Article.jsx":"5b226a88b5af","ui_kits/journal/Footer.jsx":"9dca372de45f","ui_kits/journal/Header.jsx":"08d5eac89e4b","ui_kits/journal/Home.jsx":"144c50026ded","ui_kits/journal/data.js":"01740f0a4dce"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.SolsticeDesignSystem_a0f434 = window.SolsticeDesignSystem_a0f434 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/display/Badge.jsx
try { (() => {
function Badge({
  tone = 'neutral',
  dot,
  children,
  className,
  style
}) {
  return /*#__PURE__*/React.createElement("span", {
    className: ['sl-badge', 'sl-badge--' + tone, className].filter(Boolean).join(' '),
    style: style
  }, dot && /*#__PURE__*/React.createElement("span", {
    className: "sl-badge__dot"
  }), children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Badge.jsx", error: String((e && e.message) || e) }); }

// components/display/Icon.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Icon({
  name,
  size = 18,
  color,
  style,
  className,
  label,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("i", _extends({
    className: ['sl-icon', 'icon-' + name, className].filter(Boolean).join(' '),
    style: {
      fontSize: size,
      color,
      ...style
    },
    "aria-hidden": label ? undefined : true,
    "aria-label": label,
    role: label ? 'img' : undefined
  }, rest));
}
Object.assign(__ds_scope, { Icon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Icon.jsx", error: String((e && e.message) || e) }); }

// components/actions/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const cx = (...a) => a.filter(Boolean).join(' ');
function Button({
  variant = 'primary',
  size = 'md',
  iconLeft,
  iconRight,
  fullWidth,
  children,
  className,
  as: Tag = 'button',
  ...rest
}) {
  const is = size === 'sm' ? 14 : size === 'lg' ? 18 : 16;
  return /*#__PURE__*/React.createElement(Tag, _extends({
    className: cx('sl-btn', 'sl-btn--' + variant, variant !== 'link' && 'sl-btn--' + size, fullWidth && 'sl-btn--full', className)
  }, rest), iconLeft && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: iconLeft,
    size: is
  }), children, iconRight && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: iconRight,
    size: is
  }));
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/actions/Button.jsx", error: String((e && e.message) || e) }); }

// components/actions/IconButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function IconButton({
  icon,
  label,
  variant = 'ghost',
  size = 'md',
  className,
  ...rest
}) {
  const is = size === 'sm' ? 16 : size === 'lg' ? 22 : 18;
  return /*#__PURE__*/React.createElement("button", _extends({
    "aria-label": label,
    title: label,
    className: ['sl-iconbtn', 'sl-iconbtn--' + variant, 'sl-iconbtn--' + size, className].filter(Boolean).join(' ')
  }, rest), /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: is
  }));
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/actions/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/display/ImageFrame.jsx
try { (() => {
function ImageFrame({
  src,
  alt = '',
  treatment = 'duotone',
  ratio = '4 / 3',
  grain = true,
  chord,
  caption,
  radius,
  placeholder = 'Image',
  className,
  style,
  children
}) {
  const [failed, setFailed] = React.useState(false);
  return /*#__PURE__*/React.createElement("figure", {
    "data-chord": chord,
    className: ['sl-img', 'sl-img--' + treatment, grain && 'sl-img--grain', className].filter(Boolean).join(' '),
    style: {
      aspectRatio: ratio,
      borderRadius: radius,
      background: chord ? undefined : undefined,
      ...style
    }
  }, src && !failed ? /*#__PURE__*/React.createElement("img", {
    src: src,
    alt: alt,
    loading: "lazy",
    onError: () => setFailed(true)
  }) : /*#__PURE__*/React.createElement("span", {
    className: "sl-img__empty"
  }, placeholder), caption && /*#__PURE__*/React.createElement("figcaption", {
    className: "sl-img__caption"
  }, caption), children);
}
Object.assign(__ds_scope, { ImageFrame });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/ImageFrame.jsx", error: String((e && e.message) || e) }); }

// components/display/Card.jsx
try { (() => {
function Card({
  variant = 'outlined',
  chord,
  image,
  imageRatio = '4 / 3',
  imageTreatment = 'duotone',
  eyebrow,
  title,
  text,
  footer,
  onClick,
  href,
  className,
  style,
  children
}) {
  const Tag = href ? 'a' : 'article';
  const interactive = !!(onClick || href);
  return /*#__PURE__*/React.createElement(Tag, {
    href: href,
    onClick: onClick,
    "data-chord": chord,
    className: ['sl-card', 'sl-card--' + variant, interactive && 'sl-card--interactive', className].filter(Boolean).join(' '),
    style: style
  }, image !== undefined && /*#__PURE__*/React.createElement(__ds_scope.ImageFrame, {
    src: image,
    ratio: imageRatio,
    treatment: imageTreatment,
    radius: variant === 'flat' ? 2 : 0
  }), (eyebrow || title || text || children) && /*#__PURE__*/React.createElement("div", {
    className: "sl-card__body"
  }, eyebrow && /*#__PURE__*/React.createElement("span", {
    className: "sl-eyebrow"
  }, eyebrow), title && /*#__PURE__*/React.createElement("h3", {
    className: "sl-card__title"
  }, title), text && /*#__PURE__*/React.createElement("p", {
    className: "sl-card__text"
  }, text), children), footer && /*#__PURE__*/React.createElement("div", {
    className: "sl-card__footer"
  }, footer));
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Card.jsx", error: String((e && e.message) || e) }); }

// components/display/Tag.jsx
try { (() => {
function Tag({
  selected,
  swatch,
  onRemove,
  onClick,
  children,
  className,
  style
}) {
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": !!selected,
    onClick: onClick,
    className: ['sl-tag', selected && 'sl-tag--selected', className].filter(Boolean).join(' '),
    style: style
  }, swatch && /*#__PURE__*/React.createElement("span", {
    className: "sl-tag__swatch",
    style: {
      background: swatch
    }
  }), children, onRemove && /*#__PURE__*/React.createElement("span", {
    className: "sl-tag__x",
    role: "button",
    "aria-label": "Remove",
    onClick: e => {
      e.stopPropagation();
      onRemove();
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "x",
    size: 13
  })));
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Tag.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Dialog.jsx
try { (() => {
function Dialog({
  open = true,
  onClose,
  title,
  text,
  image,
  chord,
  actions,
  children,
  inline,
  width
}) {
  React.useEffect(() => {
    if (!open || !onClose) return;
    const k = e => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [open, onClose]);
  if (!open) return null;
  const box = /*#__PURE__*/React.createElement("div", {
    role: "dialog",
    "aria-modal": "true",
    "data-chord": chord,
    className: "sl-dialog",
    style: {
      maxWidth: width
    },
    onClick: e => e.stopPropagation()
  }, onClose && /*#__PURE__*/React.createElement(__ds_scope.IconButton, {
    className: "sl-dialog__close",
    icon: "x",
    label: "Close",
    size: "sm",
    onClick: onClose
  }), image !== undefined && /*#__PURE__*/React.createElement(__ds_scope.ImageFrame, {
    src: image,
    ratio: "16 / 7",
    radius: 0
  }), /*#__PURE__*/React.createElement("div", {
    className: "sl-dialog__body"
  }, title && /*#__PURE__*/React.createElement("h2", {
    className: "sl-dialog__title"
  }, title), text && /*#__PURE__*/React.createElement("p", {
    className: "sl-dialog__text"
  }, text), children), actions && /*#__PURE__*/React.createElement("div", {
    className: "sl-dialog__actions"
  }, actions));
  return inline ? box : /*#__PURE__*/React.createElement("div", {
    className: "sl-dialog__scrim",
    onClick: onClose
  }, box);
}
Object.assign(__ds_scope, { Dialog });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Dialog.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Toast.jsx
try { (() => {
const ICONS = {
  success: 'circle-check',
  warning: 'triangle-alert',
  danger: 'circle-x',
  info: 'info',
  neutral: 'bell'
};
function Toast({
  tone = 'neutral',
  title,
  message,
  icon,
  onClose,
  action,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    role: "status",
    className: "sl-toast",
    style: style
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon || ICONS[tone],
    className: 'sl-toast__icon sl-toast__icon--' + tone
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, title && /*#__PURE__*/React.createElement("div", {
    className: "sl-toast__title"
  }, title), message && /*#__PURE__*/React.createElement("div", {
    className: "sl-toast__msg"
  }, message), action && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 8
    }
  }, action)), onClose && /*#__PURE__*/React.createElement("button", {
    className: "sl-toast__close",
    "aria-label": "Dismiss",
    onClick: onClose
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "x",
    size: 16
  })));
}
Object.assign(__ds_scope, { Toast });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Toast.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Tooltip.jsx
try { (() => {
function Tooltip({
  label,
  side = 'top',
  open,
  children
}) {
  return /*#__PURE__*/React.createElement("span", {
    className: "sl-tooltip"
  }, children, /*#__PURE__*/React.createElement("span", {
    role: "tooltip",
    className: ['sl-tooltip__bubble', 'sl-tooltip__bubble--' + side, open && 'sl-tooltip__bubble--open'].filter(Boolean).join(' ')
  }, label));
}
Object.assign(__ds_scope, { Tooltip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Tooltip.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Checkbox({
  label,
  disabled,
  className,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: ['sl-check', disabled && 'sl-check--disabled', className].filter(Boolean).join(' '),
    style: style
  }, /*#__PURE__*/React.createElement("input", _extends({
    type: "checkbox",
    disabled: disabled
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "sl-check__box"
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "check",
    size: 13
  })), label && /*#__PURE__*/React.createElement("span", null, label));
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Input({
  label,
  hint,
  error,
  iconLeft,
  iconRight,
  disabled,
  id,
  className,
  style,
  ...rest
}) {
  const fid = id || (label ? 'in-' + String(label).replace(/\W+/g, '-').toLowerCase() : undefined);
  return /*#__PURE__*/React.createElement("label", {
    className: ['sl-field', className].filter(Boolean).join(' '),
    htmlFor: fid,
    style: style
  }, label && /*#__PURE__*/React.createElement("span", {
    className: "sl-field__label"
  }, label), /*#__PURE__*/React.createElement("span", {
    className: ['sl-control', error && 'sl-control--error', disabled && 'sl-control--disabled'].filter(Boolean).join(' ')
  }, iconLeft && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: iconLeft,
    size: 16
  }), /*#__PURE__*/React.createElement("input", _extends({
    id: fid,
    disabled: disabled,
    "aria-invalid": !!error
  }, rest)), iconRight && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: iconRight,
    size: 16
  })), (error || hint) && /*#__PURE__*/React.createElement("span", {
    className: 'sl-field__hint' + (error ? ' sl-field__hint--error' : '')
  }, error || hint));
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Radio.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Radio({
  label,
  disabled,
  className,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: ['sl-check', disabled && 'sl-check--disabled', className].filter(Boolean).join(' '),
    style: style
  }, /*#__PURE__*/React.createElement("input", _extends({
    type: "radio",
    disabled: disabled
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "sl-check__box sl-check__box--radio"
  }), label && /*#__PURE__*/React.createElement("span", null, label));
}
Object.assign(__ds_scope, { Radio });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Radio.jsx", error: String((e && e.message) || e) }); }

// components/forms/Select.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Select({
  label,
  hint,
  options = [],
  disabled,
  id,
  className,
  style,
  ...rest
}) {
  const fid = id || (label ? 'sel-' + String(label).replace(/\W+/g, '-').toLowerCase() : undefined);
  return /*#__PURE__*/React.createElement("label", {
    className: ['sl-field', className].filter(Boolean).join(' '),
    htmlFor: fid,
    style: style
  }, label && /*#__PURE__*/React.createElement("span", {
    className: "sl-field__label"
  }, label), /*#__PURE__*/React.createElement("span", {
    className: 'sl-control' + (disabled ? ' sl-control--disabled' : ''),
    style: {
      paddingRight: 12
    }
  }, /*#__PURE__*/React.createElement("select", _extends({
    id: fid,
    disabled: disabled,
    style: {
      cursor: 'pointer'
    }
  }, rest), options.map(o => {
    const v = typeof o === 'string' ? {
      value: o,
      label: o
    } : o;
    return /*#__PURE__*/React.createElement("option", {
      key: v.value,
      value: v.value
    }, v.label);
  })), /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "chevron-down",
    size: 16,
    style: {
      pointerEvents: 'none'
    }
  })), hint && /*#__PURE__*/React.createElement("span", {
    className: "sl-field__hint"
  }, hint));
}
Object.assign(__ds_scope, { Select });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Select.jsx", error: String((e && e.message) || e) }); }

// components/forms/Switch.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Switch({
  label,
  disabled,
  className,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: ['sl-check', disabled && 'sl-check--disabled', className].filter(Boolean).join(' '),
    style: style
  }, /*#__PURE__*/React.createElement("input", _extends({
    type: "checkbox",
    role: "switch",
    disabled: disabled
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "sl-switch__track"
  }), label && /*#__PURE__*/React.createElement("span", null, label));
}
Object.assign(__ds_scope, { Switch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Switch.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Tabs.jsx
try { (() => {
function Tabs({
  items = [],
  value,
  onChange,
  variant = 'underline',
  className,
  style
}) {
  const [inner, setInner] = React.useState(value ?? items[0]?.id);
  const cur = value ?? inner;
  return /*#__PURE__*/React.createElement("div", {
    role: "tablist",
    className: ['sl-tabs', variant === 'pill' && 'sl-tabs--pill', className].filter(Boolean).join(' '),
    style: style
  }, items.map(it => /*#__PURE__*/React.createElement("button", {
    key: it.id,
    role: "tab",
    "aria-selected": cur === it.id,
    className: "sl-tabs__tab",
    onClick: () => {
      setInner(it.id);
      onChange && onChange(it.id);
    }
  }, it.label, it.count != null && /*#__PURE__*/React.createElement("span", {
    className: "sl-tabs__count"
  }, it.count))));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Tabs.jsx", error: String((e && e.message) || e) }); }

// ui_kits/journal/Article.jsx
try { (() => {
function JournalArticle({
  story,
  stories,
  onOpen,
  onBack
}) {
  const {
    ImageFrame,
    Button,
    IconButton,
    Tag,
    Card,
    Tooltip
  } = window.SolsticeDesignSystem_a0f434;
  const [saved, setSaved] = React.useState(false);
  const next = stories.filter(s => s.id !== story.id).slice(0, 3);
  const p = {
    margin: 0,
    fontSize: 18,
    lineHeight: 1.7,
    textWrap: 'pretty'
  };
  return /*#__PURE__*/React.createElement("main", null, /*#__PURE__*/React.createElement("section", {
    "data-chord": story.chord
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 'var(--container)',
      margin: '0 auto',
      padding: '32px var(--gutter) 0'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    size: "sm",
    iconLeft: "arrow-left",
    onClick: onBack
  }, "All stories"), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 820,
      margin: '40px auto 40px',
      textAlign: 'center',
      display: 'flex',
      flexDirection: 'column',
      gap: 18,
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      color: 'var(--text-accent)'
    }
  }, story.eyebrow, " \xB7 No. ", story.no), /*#__PURE__*/React.createElement("h1", {
    className: "t-display",
    style: {
      margin: 0,
      fontSize: 'clamp(44px,6vw,80px)',
      textWrap: 'balance'
    }
  }, story.title), /*#__PURE__*/React.createElement("p", {
    className: "t-lede",
    style: {
      margin: 0,
      color: 'var(--text-secondary)',
      maxWidth: 560
    }
  }, story.dek), /*#__PURE__*/React.createElement("span", {
    className: "t-mono",
    style: {
      fontSize: 12,
      color: 'var(--text-secondary)'
    }
  }, "By ", story.author, " \xB7 ", story.mins, " min read"))), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 'var(--container)',
      margin: '0 auto',
      padding: '0 var(--gutter)'
    }
  }, /*#__PURE__*/React.createElement(ImageFrame, {
    src: story.img,
    ratio: "21 / 9",
    radius: 0,
    caption: 'Fig. 1 — ' + story.author
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 56
    }
  })), /*#__PURE__*/React.createElement("article", {
    style: {
      maxWidth: 'var(--container)',
      margin: '0 auto',
      padding: '64px var(--gutter)',
      display: 'grid',
      gridTemplateColumns: '120px minmax(0,640px) 1fr',
      gap: 40
    }
  }, /*#__PURE__*/React.createElement("aside", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      position: 'sticky',
      top: 96,
      alignSelf: 'start'
    }
  }, /*#__PURE__*/React.createElement(Tooltip, {
    label: saved ? 'Saved' : 'Save story'
  }, /*#__PURE__*/React.createElement(IconButton, {
    icon: saved ? 'bookmark-check' : 'bookmark',
    label: "Save",
    variant: saved ? 'solid' : 'outline',
    onClick: () => setSaved(!saved)
  })), /*#__PURE__*/React.createElement(Tooltip, {
    label: "Share"
  }, /*#__PURE__*/React.createElement(IconButton, {
    icon: "share-2",
    label: "Share",
    variant: "outline"
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 24
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: p
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      float: 'left',
      fontFamily: 'var(--font-display)',
      fontSize: 88,
      lineHeight: .8,
      marginRight: 10,
      marginTop: 6,
      color: 'var(--accent)'
    }
  }, "T"), "he flats are only ever half there. At six the water has pulled back a mile, and what it leaves is a mirror the colour of weak tea, laid out under a sky that hasn't decided anything yet."), /*#__PURE__*/React.createElement("p", {
    style: p
  }, "You learn to walk it by colour rather than by map: the darker sand holds, the pale sand gives. By half past, the sun clears the dunes and everything that was grey becomes ochre, all at once, as if someone had turned a dial."), /*#__PURE__*/React.createElement("blockquote", {
    style: {
      margin: '16px 0',
      padding: 0,
      fontFamily: 'var(--font-display)',
      fontStyle: 'italic',
      fontSize: 40,
      lineHeight: 1.1,
      letterSpacing: '-0.01em',
      color: 'var(--text-accent)',
      textWrap: 'balance'
    }
  }, "\u201CEvery colour out here is borrowed from the same light.\u201D"), /*#__PURE__*/React.createElement("p", {
    style: p
  }, "That is the whole trick of the place. Nothing competes. The rust on the old posts, the lichen, the gulls' legs \u2014 each is a different volume of one warm chord."), /*#__PURE__*/React.createElement(ImageFrame, {
    src: "https://picsum.photos/id/1039/1200/800",
    chord: story.chord,
    ratio: "3 / 2",
    caption: "Fig. 2 \u2014 Channel at low water"
  }), /*#__PURE__*/React.createElement("p", {
    style: p
  }, "By eight the tide turns. You feel it before you see it: the mirror starts to move, the colour slides back to grey, and it's time to walk home by the darker sand."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      flexWrap: 'wrap',
      paddingTop: 16,
      borderTop: '1px solid var(--border-subtle)'
    }
  }, ['Coast', 'Morning', 'Low tide', 'Ochre'].map(t => /*#__PURE__*/React.createElement(Tag, {
    key: t
  }, t))))), /*#__PURE__*/React.createElement("section", {
    style: {
      borderTop: '1px solid var(--border-subtle)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 'var(--container)',
      margin: '0 auto',
      padding: '56px var(--gutter) 88px'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    className: "t-h2",
    style: {
      margin: '0 0 28px'
    }
  }, "Keep ", /*#__PURE__*/React.createElement("i", null, "reading")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3,minmax(0,1fr))',
      gap: 24
    }
  }, next.map(s => /*#__PURE__*/React.createElement(Card, {
    key: s.id,
    variant: "flat",
    image: s.img,
    eyebrow: s.eyebrow,
    title: s.title,
    onClick: () => onOpen(s)
  }))))));
}
window.JournalArticle = JournalArticle;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/journal/Article.jsx", error: String((e && e.message) || e) }); }

// ui_kits/journal/Footer.jsx
try { (() => {
function JournalFooter({
  onSubscribe
}) {
  const {
    Input,
    Button
  } = window.SolsticeDesignSystem_a0f434;
  const [email, setEmail] = React.useState('');
  return /*#__PURE__*/React.createElement("footer", {
    "data-chord": "ember"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 'var(--container)',
      margin: '0 auto',
      padding: '72px var(--gutter) 40px',
      display: 'grid',
      gridTemplateColumns: 'minmax(0,1.3fr) minmax(0,1fr)',
      gap: 48,
      alignItems: 'end'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "t-eyebrow",
    style: {
      color: 'var(--text-secondary)'
    }
  }, "The monthly letter"), /*#__PURE__*/React.createElement("h2", {
    className: "t-display",
    style: {
      margin: '12px 0 0',
      fontSize: 'clamp(40px,5vw,67px)'
    }
  }, "One photograph, one essay, ", /*#__PURE__*/React.createElement("i", null, "one colour."))), /*#__PURE__*/React.createElement("form", {
    onSubmit: e => {
      e.preventDefault();
      onSubscribe(email);
      setEmail('');
    },
    style: {
      display: 'flex',
      gap: 10,
      alignItems: 'end'
    }
  }, /*#__PURE__*/React.createElement(Input, {
    label: "Email",
    placeholder: "you@studio.com",
    type: "email",
    required: true,
    value: email,
    onChange: e => setEmail(e.target.value),
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(Button, {
    type: "submit"
  }, "Subscribe"))), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 'var(--container)',
      margin: '0 auto',
      padding: '20px var(--gutter) 28px',
      borderTop: '1px solid var(--border-subtle)',
      display: 'flex',
      justifyContent: 'space-between',
      fontFamily: 'var(--font-mono)',
      fontSize: 11,
      letterSpacing: '.08em',
      textTransform: 'uppercase',
      color: 'var(--text-secondary)'
    }
  }, /*#__PURE__*/React.createElement("span", null, "Solstice Journal \xB7 Issue 14"), /*#__PURE__*/React.createElement("span", null, "Printed by the light")));
}
window.JournalFooter = JournalFooter;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/journal/Footer.jsx", error: String((e && e.message) || e) }); }

// ui_kits/journal/Header.jsx
try { (() => {
function JournalHeader({
  onHome,
  onSubscribe,
  chord,
  setChord
}) {
  const {
    Button,
    IconButton,
    Tooltip
  } = window.SolsticeDesignSystem_a0f434;
  return /*#__PURE__*/React.createElement("header", {
    style: {
      position: 'sticky',
      top: 0,
      zIndex: 20,
      background: 'color-mix(in oklab,var(--surface-page) 86%,transparent)',
      backdropFilter: 'blur(var(--blur-glass))',
      WebkitBackdropFilter: 'blur(var(--blur-glass))',
      borderBottom: '1px solid var(--border-subtle)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 'var(--container)',
      margin: '0 auto',
      padding: '0 var(--gutter)',
      height: 68,
      display: 'flex',
      alignItems: 'center',
      gap: 32
    }
  }, /*#__PURE__*/React.createElement("a", {
    onClick: onHome,
    style: {
      cursor: 'pointer',
      textDecoration: 'none',
      color: 'var(--text-primary)',
      fontFamily: 'var(--font-display)',
      fontSize: 30,
      letterSpacing: '-0.02em'
    }
  }, "Solstice", /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--accent)'
    }
  }, ".")), /*#__PURE__*/React.createElement("nav", {
    style: {
      display: 'flex',
      gap: 24,
      fontSize: 14,
      fontWeight: 500
    }
  }, ['Stories', 'Portfolios', 'Colour', 'About'].map(n => /*#__PURE__*/React.createElement("a", {
    key: n,
    onClick: onHome,
    style: {
      cursor: 'pointer',
      color: 'var(--text-secondary)',
      textDecoration: 'none'
    }
  }, n))), /*#__PURE__*/React.createElement("div", {
    style: {
      marginLeft: 'auto',
      display: 'flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement(Tooltip, {
    label: "Search",
    side: "bottom"
  }, /*#__PURE__*/React.createElement(IconButton, {
    icon: "search",
    label: "Search"
  })), /*#__PURE__*/React.createElement(Tooltip, {
    label: chord === 'night' ? 'Day mode' : 'Night mode',
    side: "bottom"
  }, /*#__PURE__*/React.createElement(IconButton, {
    icon: chord === 'night' ? 'sun' : 'moon',
    label: "Toggle night",
    onClick: () => setChord(chord === 'night' ? 'paper' : 'night')
  })), /*#__PURE__*/React.createElement(Button, {
    size: "sm",
    onClick: onSubscribe
  }, "Subscribe"))));
}
window.JournalHeader = JournalHeader;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/journal/Header.jsx", error: String((e && e.message) || e) }); }

// ui_kits/journal/Home.jsx
try { (() => {
function JournalHome({
  stories,
  onOpen
}) {
  const {
    ImageFrame,
    Card,
    Tabs,
    Button,
    Badge
  } = window.SolsticeDesignSystem_a0f434;
  const [cat, setCat] = React.useState('all');
  const lead = stories[0];
  const list = stories.slice(1).filter(s => cat === 'all' || s.cat === cat);
  const count = c => stories.slice(1).filter(s => s.cat === c).length;
  return /*#__PURE__*/React.createElement("main", null, /*#__PURE__*/React.createElement("section", {
    "data-chord": lead.chord,
    style: {
      padding: '56px 0 64px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 'var(--container)',
      margin: '0 auto',
      padding: '0 var(--gutter)',
      display: 'grid',
      gridTemplateColumns: 'minmax(0,5fr) minmax(0,7fr)',
      gap: 48,
      alignItems: 'end'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 20,
      paddingBottom: 8
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10,
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: "accent"
  }, "Issue ", lead.no), /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      color: 'var(--text-secondary)'
    }
  }, "Winter solstice \xB7 2026")), /*#__PURE__*/React.createElement("h1", {
    className: "t-display",
    style: {
      margin: 0,
      fontSize: 'clamp(48px,6vw,84px)',
      textWrap: 'balance'
    }
  }, "What the tide ", /*#__PURE__*/React.createElement("i", null, "leaves"), " behind"), /*#__PURE__*/React.createElement("p", {
    className: "t-lede",
    style: {
      margin: 0,
      color: 'var(--text-secondary)',
      maxWidth: 440
    }
  }, lead.dek), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 12,
      alignItems: 'center',
      marginTop: 8
    }
  }, /*#__PURE__*/React.createElement(Button, {
    size: "lg",
    iconRight: "arrow-right",
    onClick: () => onOpen(lead)
  }, "Read the story"), /*#__PURE__*/React.createElement("span", {
    className: "t-mono",
    style: {
      fontSize: 12,
      color: 'var(--text-secondary)'
    }
  }, lead.author, " \xB7 ", lead.mins, " min"))), /*#__PURE__*/React.createElement("div", {
    onClick: () => onOpen(lead),
    style: {
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement(ImageFrame, {
    src: lead.img,
    ratio: "5 / 4",
    caption: 'Fig. 1 — ' + lead.title
  })))), /*#__PURE__*/React.createElement("section", {
    style: {
      maxWidth: 'var(--container)',
      margin: '0 auto',
      padding: '56px var(--gutter) 88px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'end',
      justifyContent: 'space-between',
      gap: 24,
      marginBottom: 32
    }
  }, /*#__PURE__*/React.createElement("h2", {
    className: "t-h1",
    style: {
      margin: 0
    }
  }, "Recent ", /*#__PURE__*/React.createElement("i", null, "light")), /*#__PURE__*/React.createElement(Tabs, {
    value: cat,
    onChange: setCat,
    items: [{
      id: 'all',
      label: 'All',
      count: stories.length - 1
    }, {
      id: 'essay',
      label: 'Essays',
      count: count('essay')
    }, {
      id: 'field',
      label: 'Field notes',
      count: count('field')
    }, {
      id: 'portfolio',
      label: 'Portfolios',
      count: count('portfolio')
    }]
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))',
      gap: 24
    }
  }, list.map((s, i) => /*#__PURE__*/React.createElement(Card, {
    key: s.id,
    variant: i % 3 === 1 ? 'raised' : 'flat',
    chord: i % 3 === 1 ? s.chord : undefined,
    image: s.img,
    imageRatio: i % 3 === 1 ? '1' : '4 / 3',
    eyebrow: s.eyebrow + ' · No. ' + s.no,
    title: s.title,
    text: s.dek,
    onClick: () => onOpen(s),
    footer: i % 3 === 1 ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", null, s.author), /*#__PURE__*/React.createElement("span", null, s.mins, " min")) : undefined
  })))));
}
window.JournalHome = JournalHome;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/journal/Home.jsx", error: String((e && e.message) || e) }); }

// ui_kits/journal/data.js
try { (() => {
window.JOURNAL_STORIES = [{
  id: 'tide',
  chord: 'dusk',
  img: 'https://picsum.photos/id/1015/1400/1000',
  cat: 'field',
  eyebrow: 'Field notes',
  title: 'What the tide leaves behind',
  dek: 'A walk across the flats at 6am, when the water is a rumour and the light is all ochre.',
  author: 'M. Ortega',
  mins: 8,
  no: 14
}, {
  id: 'kiln',
  chord: 'ember',
  img: 'https://picsum.photos/id/1044/1400/1000',
  cat: 'portfolio',
  eyebrow: 'Portfolio',
  title: 'Kiln light',
  dek: 'Three potters, one wood-fired kiln, and the colour of patience.',
  author: 'J. Adeyemi',
  mins: 6,
  no: 13
}, {
  id: 'grove',
  chord: 'grove',
  img: 'https://picsum.photos/id/1043/1400/1000',
  cat: 'essay',
  eyebrow: 'Essay',
  title: 'Green hours',
  dek: 'On the forty minutes after rain when every leaf holds its own lamp.',
  author: 'S. Lind',
  mins: 11,
  no: 12
}, {
  id: 'dunes',
  chord: 'ochre',
  img: 'https://picsum.photos/id/1016/1400/1000',
  cat: 'field',
  eyebrow: 'Field notes',
  title: 'Reading the dunes',
  dek: 'The wind writes in a hand only the evening sun can read.',
  author: 'A. Haddad',
  mins: 7,
  no: 11
}, {
  id: 'blue',
  chord: 'plum',
  img: 'https://picsum.photos/id/1036/1400/1000',
  cat: 'essay',
  eyebrow: 'Essay',
  title: 'Blue hour, measured',
  dek: 'Why the minutes after sunset feel longer than they are.',
  author: 'R. Ito',
  mins: 9,
  no: 10
}, {
  id: 'peak',
  chord: 'night',
  img: 'https://picsum.photos/id/1018/1400/1000',
  cat: 'portfolio',
  eyebrow: 'Portfolio',
  title: 'Alpenglow, twelve ways',
  dek: 'A single ridge photographed at dusk through a whole winter.',
  author: 'L. Moreau',
  mins: 5,
  no: 9
}];
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/journal/data.js", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Icon = __ds_scope.Icon;

__ds_ns.ImageFrame = __ds_scope.ImageFrame;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.Dialog = __ds_scope.Dialog;

__ds_ns.Toast = __ds_scope.Toast;

__ds_ns.Tooltip = __ds_scope.Tooltip;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Radio = __ds_scope.Radio;

__ds_ns.Select = __ds_scope.Select;

__ds_ns.Switch = __ds_scope.Switch;

__ds_ns.Tabs = __ds_scope.Tabs;

})();
