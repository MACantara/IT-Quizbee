# Centralized Modal System - IT Quizbee

## Overview

The IT Quizbee application now uses a centralized modal system that provides consistent, reusable modal components across the entire application. This replaces native browser `alert()` and `confirm()` dialogs with custom, styled modals.

## Features

- ✅ **Centralized Modal Templates** - Reusable modal components in `partials/modals/`
- ✅ **JavaScript Modal API** - Easy-to-use `ModalSystem` API for programmatic modals
- ✅ **Pre-built Modal Types** - Alert, Confirm, Success, Error, Warning modals
- ✅ **Custom Modal Templates** - Specialized modals for specific use cases
- ✅ **Keyboard Support** - ESC key closes modals
- ✅ **Responsive Design** - Works on all screen sizes
- ✅ **Smooth Animations** - Fade-in/fade-out transitions

## File Structure

```
templates/
├── partials/
│   └── modals/
│       ├── base_modal.html           # Base modal template (extendable)
│       ├── modal_scripts.html        # JavaScript modal system
│       ├── name_input_modal.html     # User name input modal
│       └── report_question_modal.html # Question reporting modal
└── admin/
    └── admin_base_with_sidebar.html  # Admin layout with sidebar
```

## Usage

### 1. Include Modal Scripts

Modal scripts are automatically included in `base.html`:

```html
<!-- Already included in base.html -->
{% include 'partials/modals/modal_scripts.html' %}
```

### 2. Using Built-in Modal Methods

#### Alert Modal
```javascript
// Simple alert
ModalSystem.alert('Operation completed successfully!');

// Customized alert
ModalSystem.alert('Custom message', {
    title: 'Custom Title',
    icon: 'bi-info-circle-fill',
    iconColor: 'text-blue-600',
    iconBg: 'bg-blue-100',
    buttonText: 'Got it',
    buttonClass: 'bg-blue-600 hover:bg-blue-700'
});
```

#### Confirm Modal
```javascript
// Returns a Promise<boolean>
const confirmed = await ModalSystem.confirm('Are you sure you want to delete this?');
if (confirmed) {
    // User clicked confirm
} else {
    // User clicked cancel or closed modal
}

// Customized confirm
const result = await ModalSystem.confirm('Delete this item?', {
    title: 'Confirm Deletion',
    confirmText: 'Yes, Delete',
    cancelText: 'Cancel',
    icon: 'bi-trash-fill',
    iconColor: 'text-red-600',
    iconBg: 'bg-red-100',
    confirmClass: 'bg-red-600 hover:bg-red-700'
});
```

#### Success Modal
```javascript
await ModalSystem.success('Report submitted successfully!');
```

#### Error Modal
```javascript
ModalSystem.error('Failed to save changes. Please try again.');
```

#### Warning Modal
```javascript
ModalSystem.warning('Time is running out!');
```

### 3. Using Pre-built Modal Templates

#### Name Input Modal
```jinja
{# Set configuration #}
{% set name_modal_config = {
    'mode_class': 'blue',  # blue, purple, green, orange
    'mode_title': 'Elimination Mode',
    'mode_description': 'Please enter your name to begin'
} %}

{# Include the modal #}
{% include 'partials/modals/name_input_modal.html' %}

{# Listen for name submission #}
<script>
document.addEventListener('nameSubmitted', function(e) {
    const userName = e.detail.userName;
    console.log('User entered:', userName);
    // Name is also stored in localStorage as 'quizUserName'
});
</script>
```

#### Report Question Modal
```jinja
{# Include the modal (requires results context) #}
{% include 'partials/modals/report_question_modal.html' %}

{# Open the modal from JavaScript #}
<button onclick="openReportModal('question_123', 5, 'What is Python?')">
    Report Question
</button>
```

### 4. Creating Custom Modals

#### Using Base Modal Template
```jinja
{% set modal_id = 'customModal' %}
{% set modal_title = 'Custom Modal' %}
{% set modal_subtitle = 'Subtitle text here' %}
{% set modal_icon = 'bi-star-fill' %}
{% set modal_icon_color = 'text-yellow-600' %}
{% set modal_icon_bg = 'bg-yellow-100' %}
{% set modal_size = 'lg' %}  {# sm, md, lg, xl, 2xl, 3xl, 4xl #}
{% set modal_closable = true %}

{% set modal_content %}
    <p>Your custom modal content goes here.</p>
    <form id="customForm">
        <input type="text" name="field" class="w-full px-4 py-2 border rounded-lg">
    </form>
{% endset %}

{% set modal_footer %}
    <button onclick="closeModal('customModal')" class="px-6 py-3 bg-gray-300 rounded-lg">
        Cancel
    </button>
    <button onclick="submitCustomForm()" class="px-6 py-3 bg-blue-600 text-white rounded-lg">
        Submit
    </button>
{% endset %}

{% include 'partials/modals/base_modal.html' %}
```

#### Programmatic Modal Creation
```javascript
// Open a modal
openModal('modalId');

// Close a modal
closeModal('modalId');

// Or use the ModalSystem object
ModalSystem.openModal('modalId');
ModalSystem.closeModal('modalId');
```

## Styling Classes

### Color Themes

| Theme | Icon Color | Background | Button |
|-------|-----------|------------|--------|
| Blue | `text-blue-600` | `bg-blue-100` | `bg-blue-600 hover:bg-blue-700` |
| Purple | `text-purple-600` | `bg-purple-100` | `bg-purple-600 hover:bg-purple-700` |
| Green | `text-green-600` | `bg-green-100` | `bg-green-600 hover:bg-green-700` |
| Orange | `text-orange-600` | `bg-orange-100` | `bg-orange-600 hover:bg-orange-700` |
| Red | `text-red-600` | `bg-red-100` | `bg-red-600 hover:bg-red-700` |
| Yellow | `text-yellow-600` | `bg-yellow-100` | `bg-yellow-600 hover:bg-yellow-700` |

### Modal Sizes

- `sm` - 24rem (384px)
- `md` - 28rem (448px) - Default
- `lg` - 32rem (512px)
- `xl` - 36rem (576px)
- `2xl` - 42rem (672px)
- `3xl` - 48rem (768px)
- `4xl` - 56rem (896px)

## Migration from Native Dialogs

### Before (Native)
```javascript
if (confirm('Are you sure?')) {
    deleteItem();
}

alert('Operation completed!');
```

### After (Modal System)
```javascript
const confirmed = await ModalSystem.confirm('Are you sure?');
if (confirmed) {
    deleteItem();
}

await ModalSystem.success('Operation completed!');
```

## Admin Dashboard Updates

The admin section now includes:

1. **Sidebar Navigation** - Fixed sidebar with:
   - Dashboard link
   - Question Reports link (with pending count badge)
   - Analytics quick links
   - System links (API Health, Export Data)
   - Logout button

2. **Organized Sections** - Dashboard is now organized into:
   - Overview (stats cards)
   - Performance Metrics (charts)
   - Statistics Breakdown
   - Question Analytics
   - Recent Activity

3. **Consistent Modals** - All confirm/alert dialogs use the modal system

## Files Updated

### New Files Created
- `templates/partials/modals/base_modal.html` - Base modal template
- `templates/partials/modals/modal_scripts.html` - JavaScript modal system
- `templates/partials/modals/name_input_modal.html` - Name input modal
- `templates/partials/modals/report_question_modal.html` - Report modal
- `templates/admin/admin_base_with_sidebar.html` - Admin layout with sidebar

### Files Modified
- `templates/base.html` - Added modal scripts include
- `templates/admin/admin_dashboard.html` - Uses sidebar layout, organized sections
- `templates/admin/question_reports.html` - Uses sidebar layout, modal confirms
- `templates/quiz/results.html` - Uses centralized report modal
- `templates/quiz/elimination_mode.html` - Uses centralized name modal
- `templates/quiz/finals_mode.html` - Uses centralized name modal (in progress)
- `templates/quiz/quiz.html` - Uses centralized name modal (in progress)

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## Future Enhancements

- [ ] Modal stacking (multiple modals open)
- [ ] Custom animations
- [ ] Loading/spinner modal
- [ ] Form validation modals
- [ ] Image/media preview modals
- [ ] Draggable modals
- [ ] Modal size transitions

## Troubleshooting

### Modal doesn't close
- Check if `closeModal()` is being called
- Verify modal ID matches
- Check console for JavaScript errors

### Confirm doesn't work
- Make sure you're using `await` with `ModalSystem.confirm()`
- Verify the function is async: `async function myFunction() { ... }`

### Styles not applied
- Ensure Tailwind CSS is loaded
- Check if custom classes are properly defined
- Verify Bootstrap Icons are included

## Examples in Codebase

- **Alert**: `templates/admin/question_reports.html` - Success/error alerts
- **Confirm**: `templates/admin/question_reports.html` - Delete confirmation
- **Name Modal**: `templates/quiz/elimination_mode.html` - User name input
- **Report Modal**: `templates/quiz/results.html` - Question reporting

## Best Practices

1. **Always use await with confirm**
   ```javascript
   const confirmed = await ModalSystem.confirm('message');
   ```

2. **Provide context in modal titles**
   ```javascript
   ModalSystem.confirm('Delete question #42?', {
       title: 'Confirm Deletion',
       confirmText: 'Delete'
   });
   ```

3. **Use appropriate modal types**
   - `success` - Operations completed successfully
   - `error` - Operations failed
   - `warning` - Important information, time running out
   - `confirm` - User needs to make a decision

4. **Keep messages concise**
   - Short, clear messages
   - Action-oriented button text
   - Avoid technical jargon

5. **Provide feedback**
   - Always show result after confirm action
   - Use success/error modals after operations
