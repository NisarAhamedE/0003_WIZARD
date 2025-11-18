# Sample Wizards with Conditional Dependencies - User Guide

## Overview
Five comprehensive wizards have been created to showcase the conditional filtering feature across different use cases:
1. **IT Support Ticket System** - Helpdesk/IT support workflow
2. **Custom Laptop Configuration** - E-commerce product configurator
3. **International Shipping Request** - Logistics and shipping
4. **Job Application Form** - HR recruitment workflow
5. **Customer Satisfaction Survey** - Feedback and surveys

All wizards are published and ready to test at **http://localhost:3000**

---

## Wizard 1: IT Support Ticket System
**Use Case:** IT helpdesk and support ticket management

### Flow:
1. **Issue Type** - Select category (Hardware, Software, Network, Account)
2. **Hardware Details** - Shown only if Hardware selected
3. **Software Details** - Shown only if Software selected
4. **Priority & Description** - Set urgency and describe issue

### Dependencies Implemented:
- **show_if**: Hardware detail options appear ONLY when "Hardware Problem" is selected in step 1
- **show_if**: Software detail options appear ONLY when "Software Issue" is selected in step 1
- This ensures users only see relevant troubleshooting questions based on their issue type

### Test Scenario:
1. Start the wizard
2. Select "Hardware Problem" → Step 2 shows hardware device options
3. Go back, select "Software Issue" → Step 2 now shows software application options
4. Select "Network/Connectivity" → Step 2 shows no options (skippable)

---

## Wizard 2: Custom Laptop Configuration
**Use Case:** E-commerce product configurator for laptops

### Flow:
1. **Laptop Type** - Select primary use (Gaming, Business, Student, Creative)
2. **Processor** - Choose CPU (Intel i5/i7/i9, AMD Ryzen)
3. **Graphics Card** - Select GPU (Integrated, RTX 3050/3060/4060/4070)
4. **Memory & Storage** - Configure RAM (8/16/32/64GB) and SSD (256GB-2TB)
5. **Add-ons** - Optional accessories (warranty, bag, mouse, monitor)

### Dependencies Implemented:
- **disable_if**: Integrated Graphics disabled when "Gaming" or "Creative Work" selected
  - Gaming and creative work require dedicated graphics cards
- **hide_if**: 8GB RAM hidden when "Gaming" selected
  - Gaming laptops need minimum 16GB RAM
- Ensures realistic configurations and prevents invalid combinations

### Test Scenario:
1. Select "Gaming" laptop
   → Integrated Graphics becomes disabled/grayed out
   → 8GB RAM option disappears
2. Select "Business/Work"
   → All graphics options available
   → All RAM options visible

---

## Wizard 3: International Shipping Request
**Use Case:** Logistics and shipping with customs/special handling

### Flow:
1. **Shipment Type** - Category (Documents, Packages, Freight, Perishables, Hazmat)
2. **Destination** - Region (Domestic, Canada/Mexico, Europe, Asia-Pacific, Other)
3. **Customs Information** - Declaration type (Gift, Commercial, Personal, Sample)
4. **Special Handling** - Temperature control & hazmat classification
5. **Delivery Options** - Speed and additional services

### Dependencies Implemented:
- **hide_if**: Customs options hidden when "Domestic (USA)" selected
  - No customs needed for domestic shipments
- **show_if**: Temperature control options shown ONLY for "Perishables"
  - Only perishables need refrigeration/freezing
- **show_if**: Hazmat classification shown ONLY for "Hazardous Materials"
  - Class 3/8/9 classification only relevant for hazmat
- **disable_if**: Economy delivery disabled for "Perishables" and "Hazmat"
  - These require expedited shipping

### Test Scenario:
1. Select "Perishables" shipment
   → Step 4 shows temperature control options (Refrigerated, Frozen, Ambient)
   → Economy delivery becomes disabled in Step 5
2. Select "Documents"
   → Step 4 shows no special handling options (skippable)
3. Select "Domestic" destination
   → Step 3 (Customs) disappears entirely

---

## Wizard 4: Job Application Form
**Use Case:** HR recruitment and job applications

### Flow:
1. **Position Information** - Role and employment type
2. **Experience** - Years of relevant experience
3. **Technical Skills** - Programming languages and frameworks
4. **Design Portfolio** - Portfolio URL and design tools
5. **Availability** - Start date and work arrangement preference

### Dependencies Implemented:
- **show_if**: Technical Skills step shown ONLY for Software Engineer or Senior Software Engineer
  - Non-technical roles don't need programming questions
- **show_if**: Design Portfolio step shown ONLY for UX Designer position
  - Only designers need to provide portfolio
- **disable_if**: Full-time employment disabled when "Intern" position selected
  - Interns typically work part-time or contract
- **hide_if**: "No experience" and "1-2 years" hidden for Senior Software Engineer
  - Senior roles require 3+ years experience

### Test Scenario:
1. Select "Software Engineer"
   → Step 3 shows programming language questions
   → Step 4 (Design Portfolio) skipped
2. Select "UX Designer"
   → Step 3 (Technical Skills) skipped
   → Step 4 shows portfolio and design tools
3. Select "Sales Representative"
   → Both Step 3 and 4 skipped (not technical role)
4. Select "Intern" position
   → "Full-time" employment option becomes disabled
5. Select "Senior Software Engineer"
   → "No experience" option disappears from experience list

---

## Wizard 5: Customer Satisfaction Survey
**Use Case:** Customer feedback and satisfaction surveys

### Flow:
1. **Overall Experience** - Satisfaction rating (Very Satisfied → Very Dissatisfied)
2. **What went well** - Positive aspects (fast response, quality, etc.)
3. **Areas for improvement** - Issues and improvement text
4. **Recommendation** - Would recommend to a friend?

### Dependencies Implemented:
- **show_if**: "What went well" step shown ONLY for "Very Satisfied" or "Satisfied"
  - Only ask about positives if customer is happy
- **show_if**: "Areas for improvement" shown ONLY for "Dissatisfied" or "Very Dissatisfied"
  - Only ask what went wrong if customer is unhappy
- Creates smart branching based on sentiment

### Test Scenario:
1. Select "Very Satisfied"
   → Step 2 asks "What did you like most?"
   → Step 3 (improvements) skipped
2. Select "Dissatisfied"
   → Step 2 (positives) skipped
   → Step 3 asks "What could we improve?" with text input
3. Select "Neutral"
   → Both Step 2 and 3 skipped

---

## Dependency Types Used

### 1. show_if (Most Common)
**Usage:** Option appears ONLY when dependency is selected
**Examples:**
- Hardware details shown when "Hardware Problem" selected
- Temperature control shown when "Perishables" selected
- Tech skills shown when "Software Engineer" selected

### 2. hide_if
**Usage:** Option disappears when dependency is selected
**Examples:**
- Customs info hidden for domestic shipments
- 8GB RAM hidden for gaming laptops
- Low experience hidden for senior positions

### 3. disable_if
**Usage:** Option becomes disabled/grayed out when dependency is selected
**Examples:**
- Integrated graphics disabled for gaming/creative
- Economy delivery disabled for perishables/hazmat
- Full-time employment disabled for interns

### 4. require_if
**Usage:** Makes option set required when dependency is selected
**Examples:**
- Student ID becomes required when "Yes, I'm a student" selected (not in current wizards but available)

---

## Testing Guide

### Basic Testing:
1. Visit http://localhost:3000
2. Click "Available Wizards" in the navigation
3. Choose any of the 5 wizards
4. Click "Start Wizard"
5. Progress through the steps and observe how options appear/disappear/disable based on your selections

### Admin Testing:
1. Login as admin (username: `admin`, password: `Admin@123`)
2. Go to "Wizard Builder"
3. Click "Edit Wizard" on any of the 5 wizards
4. Expand an option accordion
5. Scroll to "Conditional Dependencies" section
6. See the configured dependencies
7. Try adding new dependencies

### Dependency Verification:
Each wizard includes a comments section in the scripts showing exactly which dependencies were created. You can verify by:
1. Editing wizard in Wizard Builder
2. Expanding options with dependency badges
3. Checking the dependency configuration matches the documentation

---

## Database State

After running the creation scripts, your database contains:
- **5 Wizards** - All published and ready to use
- **~80 Options** - Across all steps and option sets
- **~30 Dependencies** - Configured across all wizards
- **0 Sessions** - Fresh start, no user sessions yet
- **0 Templates** - Ready for users to create templates

---

## Script Files

Three Python scripts were used to create these wizards:

### 1. `create_sample_wizards.py`
Creates the first 3 wizards:
- IT Support Ticket System (with hardware/software dependencies)
- Custom Laptop Configuration (with graphics/RAM dependencies)
- International Shipping Request (with customs/special handling dependencies)

### 2. `create_more_wizards.py`
Creates the last 2 wizards:
- Job Application Form (with role-based dependencies)
- Customer Satisfaction Survey (with sentiment-based dependencies)

### 3. `add_dependencies.py`
Adds any missing dependencies to existing wizards (safety script)

**Usage:**
```bash
python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('create_sample_wizards.py', encoding='utf-8').read())"
python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); exec(open('create_more_wizards.py', encoding='utf-8').read())"
```

---

## Common Issues & Solutions

### Issue: Dependencies not showing in player
**Solution:** Dependencies only apply to options that have been saved with IDs. If you create new options in builder, save the wizard first before adding dependencies.

### Issue: All options showing regardless of selection
**Solution:** Check that dependencies are using correct option IDs. Use Wizard Builder to verify dependency configuration.

### Issue: Wizard Builder shows "No other options available"
**Solution:** Dependencies can only reference options from previous steps. Create earlier steps first, then add dependencies to later options.

### Issue: Multiple dependencies on same option
**Solution:** This is supported! An option can have multiple dependencies. All are evaluated independently.

---

## Next Steps

1. **Test Each Wizard**: Walk through all 5 wizards as a user
2. **Create Sessions**: Complete sessions to generate data
3. **Create Templates**: Save favorite configurations as templates
4. **View Analytics**: Check admin analytics to see wizard usage
5. **Modify Dependencies**: Edit wizards in builder to add/remove dependencies
6. **Create New Wizards**: Use these as examples for your own wizards

---

## Technical Notes

### Dependency Evaluation Logic
```typescript
// From WizardPlayerPage.tsx
const getAllSelectedOptionIds = () => {
  // Collects all selected option IDs from current and previous steps
}

const shouldShowOption = (option) => {
  // Checks show_if and hide_if dependencies
  // Returns false if any hide_if is met OR any show_if is NOT met
}

const shouldDisableOption = (option) => {
  // Checks disable_if dependencies
  // Returns true if any disable_if condition is met
}

const isOptionSetRequired = (optionSet) => {
  // Checks require_if dependencies on all options
  // Returns true if base required OR any option has met require_if
}
```

### Dependency Direction Rules
- Options can only depend on options from **earlier** steps
- Options can depend on options from earlier option sets in the **same** step
- This prevents circular dependencies
- Ensures logical forward flow

---

## Summary

✅ **5 Wizards Created**
- IT Support (4 steps, show_if dependencies)
- Laptop Config (5 steps, disable_if + hide_if dependencies)
- Shipping (5 steps, hide_if + show_if + disable_if dependencies)
- Job Application (5 steps, show_if + disable_if + hide_if dependencies)
- Feedback Survey (4 steps, show_if dependencies)

✅ **All Dependency Types Demonstrated**
- show_if, hide_if, disable_if, require_if (available)

✅ **Multiple Use Cases Covered**
- IT/Technology, E-commerce, Logistics, HR, Customer Service

✅ **Ready for Testing**
- Visit: http://localhost:3000
- Admin login: admin / Admin@123
- User registration available

**Happy Testing!** 🎉
