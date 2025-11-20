# Flutter Mobile App Implementation Plan
## Multi-Wizard Platform - Mobile Edition

---

## Executive Summary

This document outlines a comprehensive implementation plan for developing a Flutter mobile application that implements **Wizard Run** and **Store Wizard** functionalities. The mobile app will connect to the existing PostgreSQL database via the FastAPI backend APIs, allowing users to execute wizards and manage stored wizard runs on-the-go.

### Key Features
- **Run Wizard**: Execute published wizards with all 12 selection types
- **Store Wizard**: Access, view, and manage stored wizard runs
- **My Runs**: Track in-progress and completed runs
- **User Authentication**: JWT-based authentication
- **Offline Support**: Cache wizard data for offline execution
- **File Uploads**: Support file uploads during wizard execution
- **Progress Tracking**: Auto-save and resume wizard runs

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [API Integration Strategy](#api-integration-strategy)
5. [Database Schema (Existing)](#database-schema-existing)
6. [Implementation Phases](#implementation-phases)
7. [Feature Specifications](#feature-specifications)
8. [UI/UX Design Guidelines](#uiux-design-guidelines)
9. [Security Considerations](#security-considerations)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Plan](#deployment-plan)
12. [Development Timeline](#development-timeline)

---

## 1. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────┐
│         Flutter Mobile App (Dart)            │
│  ┌────────────────────────────────────────┐ │
│  │   Presentation Layer (UI/UX)           │ │
│  │  - Screens, Widgets, Themes            │ │
│  └────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────┐ │
│  │   Business Logic Layer                 │ │
│  │  - BLoC/Provider State Management      │ │
│  │  - Use Cases, Services                 │ │
│  └────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────┐ │
│  │   Data Layer                           │ │
│  │  - Repositories, API Clients           │ │
│  │  - Local Storage (SQLite/Hive)         │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                     ↕ HTTPS
┌─────────────────────────────────────────────┐
│    FastAPI Backend (Existing)                │
│  - REST API Endpoints                        │
│  - JWT Authentication                        │
│  - File Upload Handling                      │
└─────────────────────────────────────────────┘
                     ↕
┌─────────────────────────────────────────────┐
│    PostgreSQL Database (Existing)            │
│  - wizarddb                                  │
└─────────────────────────────────────────────┘
```

### Architecture Patterns

- **Clean Architecture**: Separation of concerns with clear layers
- **BLoC Pattern**: Business Logic Component for state management
- **Repository Pattern**: Abstract data sources
- **Dependency Injection**: Using `get_it` package

---

## 2. Technology Stack

### Core Framework
- **Flutter SDK**: 3.16+ (latest stable)
- **Dart**: 3.0+

### State Management
- **flutter_bloc**: ^8.1.0 (BLoC pattern implementation)
- **equatable**: ^2.0.5 (Value equality)

### HTTP & API
- **dio**: ^5.4.0 (HTTP client with interceptors)
- **retrofit**: ^4.0.3 (Type-safe API client generator)
- **json_annotation**: ^4.8.1 (JSON serialization)

### Local Storage
- **hive**: ^2.2.3 (Fast NoSQL database)
- **hive_flutter**: ^1.1.0
- **shared_preferences**: ^2.2.2 (Simple key-value storage)

### Authentication
- **flutter_secure_storage**: ^9.0.0 (Secure JWT token storage)

### UI Components
- **flutter_svg**: ^2.0.9 (SVG rendering)
- **cached_network_image**: ^3.3.1 (Image caching)
- **shimmer**: ^3.0.0 (Loading skeletons)
- **flutter_spinkit**: ^5.2.0 (Loading indicators)

### Forms & Validation
- **flutter_form_builder**: ^9.1.1 (Dynamic form builder)
- **form_builder_validators**: ^9.1.0 (Validators)

### File Handling
- **file_picker**: ^6.1.1 (File selection)
- **image_picker**: ^1.0.7 (Image capture)
- **path_provider**: ^2.1.2 (Directory paths)

### Rich Text
- **flutter_quill**: ^9.0.0 (Rich text editor)

### Date/Time
- **intl**: ^0.18.1 (Internationalization)

### Utilities
- **get_it**: ^7.6.4 (Dependency injection)
- **dartz**: ^0.10.1 (Functional programming)
- **connectivity_plus**: ^5.0.2 (Network connectivity)
- **uuid**: ^4.3.3 (UUID generation)

### Development Tools
- **build_runner**: ^2.4.7 (Code generation)
- **json_serializable**: ^6.7.1 (JSON code generation)
- **retrofit_generator**: ^7.0.8 (API client generation)
- **flutter_launcher_icons**: ^0.13.1 (App icons)
- **flutter_native_splash**: ^2.3.9 (Splash screen)

### Testing
- **flutter_test**: SDK
- **mockito**: ^5.4.4 (Mocking)
- **bloc_test**: ^9.1.5 (BLoC testing)

---

## 3. Project Structure

```
flutter_wizard_app/
├── android/                    # Android native code
├── ios/                        # iOS native code
├── lib/
│   ├── main.dart               # Entry point
│   ├── app.dart                # App widget with routing
│   │
│   ├── core/                   # Core utilities
│   │   ├── constants/
│   │   │   ├── api_constants.dart
│   │   │   ├── app_constants.dart
│   │   │   └── storage_constants.dart
│   │   ├── errors/
│   │   │   ├── exceptions.dart
│   │   │   └── failures.dart
│   │   ├── network/
│   │   │   ├── dio_client.dart
│   │   │   └── network_info.dart
│   │   ├── storage/
│   │   │   ├── local_storage.dart
│   │   │   └── secure_storage.dart
│   │   ├── theme/
│   │   │   ├── app_colors.dart
│   │   │   ├── app_theme.dart
│   │   │   └── app_text_styles.dart
│   │   └── utils/
│   │       ├── date_formatter.dart
│   │       ├── validators.dart
│   │       └── extensions.dart
│   │
│   ├── data/                   # Data layer
│   │   ├── datasources/
│   │   │   ├── local/
│   │   │   │   ├── wizard_local_datasource.dart
│   │   │   │   └── auth_local_datasource.dart
│   │   │   └── remote/
│   │   │       ├── wizard_remote_datasource.dart
│   │   │       ├── wizard_run_remote_datasource.dart
│   │   │       └── auth_remote_datasource.dart
│   │   ├── models/
│   │   │   ├── wizard_model.dart
│   │   │   ├── wizard_run_model.dart
│   │   │   ├── step_model.dart
│   │   │   ├── option_set_model.dart
│   │   │   ├── user_model.dart
│   │   │   └── response_models.dart
│   │   └── repositories/
│   │       ├── wizard_repository_impl.dart
│   │       ├── wizard_run_repository_impl.dart
│   │       └── auth_repository_impl.dart
│   │
│   ├── domain/                 # Business logic layer
│   │   ├── entities/
│   │   │   ├── wizard.dart
│   │   │   ├── wizard_run.dart
│   │   │   ├── step.dart
│   │   │   ├── option_set.dart
│   │   │   └── user.dart
│   │   ├── repositories/
│   │   │   ├── wizard_repository.dart
│   │   │   ├── wizard_run_repository.dart
│   │   │   └── auth_repository.dart
│   │   └── usecases/
│   │       ├── auth/
│   │       │   ├── login_usecase.dart
│   │       │   ├── logout_usecase.dart
│   │       │   └── check_auth_usecase.dart
│   │       ├── wizard/
│   │       │   ├── get_wizards_usecase.dart
│   │       │   ├── get_wizard_by_id_usecase.dart
│   │       │   └── search_wizards_usecase.dart
│   │       └── wizard_run/
│   │           ├── create_run_usecase.dart
│   │           ├── update_run_usecase.dart
│   │           ├── complete_run_usecase.dart
│   │           ├── get_stored_runs_usecase.dart
│   │           ├── get_in_progress_runs_usecase.dart
│   │           ├── save_step_response_usecase.dart
│   │           └── upload_file_usecase.dart
│   │
│   ├── presentation/           # Presentation layer
│   │   ├── blocs/
│   │   │   ├── auth/
│   │   │   │   ├── auth_bloc.dart
│   │   │   │   ├── auth_event.dart
│   │   │   │   └── auth_state.dart
│   │   │   ├── wizard/
│   │   │   │   ├── wizard_bloc.dart
│   │   │   │   ├── wizard_event.dart
│   │   │   │   └── wizard_state.dart
│   │   │   ├── wizard_run/
│   │   │   │   ├── wizard_run_bloc.dart
│   │   │   │   ├── wizard_run_event.dart
│   │   │   │   └── wizard_run_state.dart
│   │   │   └── store/
│   │   │       ├── store_bloc.dart
│   │   │       ├── store_event.dart
│   │   │       └── store_state.dart
│   │   ├── screens/
│   │   │   ├── auth/
│   │   │   │   ├── login_screen.dart
│   │   │   │   └── register_screen.dart
│   │   │   ├── home/
│   │   │   │   ├── home_screen.dart
│   │   │   │   └── dashboard_screen.dart
│   │   │   ├── wizard/
│   │   │   │   ├── wizard_list_screen.dart
│   │   │   │   ├── wizard_detail_screen.dart
│   │   │   │   └── wizard_player_screen.dart
│   │   │   ├── runs/
│   │   │   │   ├── my_runs_screen.dart
│   │   │   │   └── run_detail_screen.dart
│   │   │   └── store/
│   │   │       ├── store_screen.dart
│   │   │       └── stored_run_detail_screen.dart
│   │   ├── widgets/
│   │   │   ├── common/
│   │   │   │   ├── app_button.dart
│   │   │   │   ├── app_text_field.dart
│   │   │   │   ├── loading_indicator.dart
│   │   │   │   └── error_widget.dart
│   │   │   ├── wizard/
│   │   │   │   ├── wizard_card.dart
│   │   │   │   ├── step_progress_indicator.dart
│   │   │   │   └── wizard_navigation.dart
│   │   │   └── option_sets/
│   │   │       ├── single_select_widget.dart
│   │   │       ├── multiple_select_widget.dart
│   │   │       ├── text_input_widget.dart
│   │   │       ├── number_input_widget.dart
│   │   │       ├── date_input_widget.dart
│   │   │       ├── time_input_widget.dart
│   │   │       ├── datetime_input_widget.dart
│   │   │       ├── rating_widget.dart
│   │   │       ├── slider_widget.dart
│   │   │       ├── color_picker_widget.dart
│   │   │       ├── file_upload_widget.dart
│   │   │       └── rich_text_widget.dart
│   │   └── routes/
│   │       ├── app_router.dart
│   │       └── route_names.dart
│   │
│   └── injection_container.dart  # Dependency injection setup
│
├── test/                       # Unit & widget tests
├── integration_test/           # Integration tests
├── assets/                     # Images, fonts, etc.
│   ├── images/
│   ├── icons/
│   └── fonts/
├── pubspec.yaml                # Dependencies
└── README.md
```

---

## 4. API Integration Strategy

### Backend Base URL Configuration

```dart
// lib/core/constants/api_constants.dart
class ApiConstants {
  // Update this to your actual backend URL
  static const String baseUrl = 'http://YOUR_SERVER_IP:8000/api/v1';

  // Auth endpoints
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';

  // Wizard endpoints
  static const String wizardsEndpoint = '/wizards';
  static const String wizardByIdEndpoint = '/wizards/{id}';

  // Wizard Run endpoints
  static const String wizardRunsEndpoint = '/wizard-runs';
  static const String createRunEndpoint = '/wizard-runs';
  static const String inProgressRunsEndpoint = '/wizard-runs/in-progress';
  static const String completedRunsEndpoint = '/wizard-runs/completed';
  static const String storedRunsEndpoint = '/wizard-runs/stored';
  static const String favoriteRunsEndpoint = '/wizard-runs/favorites';
  static const String runStatsEndpoint = '/wizard-runs/stats';
  static const String completeRunEndpoint = '/wizard-runs/{id}/complete';
  static const String updateProgressEndpoint = '/wizard-runs/{id}/progress';

  // Step response endpoints
  static const String createStepResponseEndpoint = '/wizard-runs/{runId}/steps';

  // Option set response endpoints
  static const String createOptionSetResponseEndpoint = '/wizard-runs/{runId}/option-sets';

  // File upload endpoint
  static const String uploadFileEndpoint = '/wizard-runs/{runId}/upload';

  // Share endpoints
  static const String createShareEndpoint = '/wizard-runs/{runId}/share';
}
```

### API Client Setup with Retrofit

```dart
// lib/data/datasources/remote/api_client.dart
import 'package:retrofit/retrofit.dart';
import 'package:dio/dio.dart';

part 'api_client.g.dart';

@RestApi()
abstract class ApiClient {
  factory ApiClient(Dio dio, {String baseUrl}) = _ApiClient;

  // Auth
  @POST('/auth/login')
  Future<LoginResponse> login(@Body() LoginRequest request);

  // Wizards
  @GET('/wizards')
  Future<List<WizardModel>> getWizards(
    @Query('published_only') bool publishedOnly,
    @Query('skip') int skip,
    @Query('limit') int limit,
  );

  @GET('/wizards/{id}')
  Future<WizardModel> getWizardById(@Path('id') String id);

  // Wizard Runs
  @POST('/wizard-runs')
  Future<WizardRunModel> createWizardRun(@Body() CreateWizardRunRequest request);

  @GET('/wizard-runs/{id}')
  Future<WizardRunDetailModel> getWizardRun(@Path('id') String id);

  @GET('/wizard-runs/in-progress')
  Future<List<WizardRunModel>> getInProgressRuns();

  @GET('/wizard-runs/stored')
  Future<List<WizardRunModel>> getStoredRuns(
    @Query('skip') int skip,
    @Query('limit') int limit,
  );

  @GET('/wizard-runs/stats')
  Future<WizardRunStatsModel> getRunStats();

  @POST('/wizard-runs/{id}/complete')
  Future<WizardRunModel> completeWizardRun(
    @Path('id') String id,
    @Body() CompleteWizardRunRequest request,
  );

  @POST('/wizard-runs/{id}/progress')
  Future<WizardRunModel> updateRunProgress(
    @Path('id') String id,
    @Body() UpdateProgressRequest request,
  );

  // Step Responses
  @POST('/wizard-runs/{runId}/steps')
  Future<StepResponseModel> createStepResponse(
    @Path('runId') String runId,
    @Body() CreateStepResponseRequest request,
  );

  // Option Set Responses
  @POST('/wizard-runs/{runId}/option-sets')
  Future<OptionSetResponseModel> createOptionSetResponse(
    @Path('runId') String runId,
    @Body() CreateOptionSetResponseRequest request,
  );

  // File Upload
  @POST('/wizard-runs/{runId}/upload')
  @MultiPart()
  Future<FileUploadModel> uploadFile(
    @Path('runId') String runId,
    @Query('option_set_response_id') String optionSetResponseId,
    @Part(name: 'file') File file,
  );
}
```

### Dio Configuration with JWT Interceptor

```dart
// lib/core/network/dio_client.dart
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class DioClient {
  final Dio _dio;
  final FlutterSecureStorage _secureStorage;

  DioClient(this._dio, this._secureStorage) {
    _dio
      ..options.baseUrl = ApiConstants.baseUrl
      ..options.connectTimeout = const Duration(seconds: 30)
      ..options.receiveTimeout = const Duration(seconds: 30)
      ..options.headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
      ..interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) async {
            // Add JWT token to headers
            final token = await _secureStorage.read(key: 'access_token');
            if (token != null) {
              options.headers['Authorization'] = 'Bearer $token';
            }
            return handler.next(options);
          },
          onError: (error, handler) async {
            if (error.response?.statusCode == 401) {
              // Token expired, logout user
              await _secureStorage.delete(key: 'access_token');
              // Navigate to login screen
            }
            return handler.next(error);
          },
        ),
      )
      ..interceptors.add(LogInterceptor(
        requestBody: true,
        responseBody: true,
      ));
  }

  Dio get dio => _dio;
}
```

---

## 5. Database Schema (Existing)

### Key Tables Used by Mobile App

The mobile app will interact with these existing PostgreSQL tables via the FastAPI backend:

#### **wizards** table
- Core wizard definitions (name, description, settings)
- Fields: `id`, `name`, `description`, `category_id`, `is_published`, `difficulty_level`, `estimated_time`, `tags`

#### **steps** table
- Wizard steps with ordering
- Fields: `id`, `wizard_id`, `name`, `description`, `step_order`, `is_required`, `is_skippable`

#### **option_sets** table
- Input fields within steps
- Fields: `id`, `step_id`, `name`, `selection_type`, `is_required`, `display_order`
- **Selection Types**: `single_select`, `multiple_select`, `text_input`, `number_input`, `date_input`, `time_input`, `datetime_input`, `rating`, `slider`, `color_picker`, `file_upload`, `rich_text`

#### **options** table
- Predefined options for single/multiple select
- Fields: `id`, `option_set_id`, `label`, `value`, `display_order`

#### **wizard_runs** table
- User wizard execution tracking
- Fields: `id`, `wizard_id`, `user_id`, `run_name`, `status`, `current_step_index`, `progress_percentage`, `started_at`, `completed_at`, `is_stored`, `is_favorite`

#### **wizard_run_step_responses** table
- Step-level completion tracking
- Fields: `id`, `run_id`, `step_id`, `step_index`, `completed`, `time_spent_seconds`

#### **wizard_run_option_set_responses** table
- User responses to option sets (JSONB flexible storage)
- Fields: `id`, `run_id`, `step_response_id`, `option_set_id`, `response_value` (JSONB), `selected_options` (UUID[])

#### **wizard_run_file_uploads** table
- File upload references
- Fields: `id`, `run_id`, `option_set_response_id`, `file_name`, `file_path`, `file_size`, `file_type`

#### **wizard_run_shares** table
- Share links for completed runs
- Fields: `id`, `run_id`, `share_token`, `share_type`, `access_count`

#### **users** table
- User authentication and profiles
- Fields: `id`, `username`, `email`, `hashed_password`, `role_id`, `is_active`

---

## 6. Implementation Phases

### Phase 1: Foundation & Authentication (Week 1-2)

**Objectives:**
- Set up Flutter project structure
- Implement core utilities and configurations
- Build authentication system
- Create base UI components

**Tasks:**
1. Initialize Flutter project with clean architecture structure
2. Configure dependencies in `pubspec.yaml`
3. Set up dependency injection with `get_it`
4. Implement Dio HTTP client with JWT interceptor
5. Create secure storage service for tokens
6. Build authentication BLoC (login, logout, register)
7. Design and implement login/register screens
8. Create theme and design system
9. Implement splash screen with auth check
10. Set up app routing with route guards

**Deliverables:**
- Working authentication flow
- Secure token storage
- Base app navigation
- Theme system

---

### Phase 2: Wizard Listing & Details (Week 3-4)

**Objectives:**
- Display published wizards
- Show wizard details
- Implement search and filters

**Tasks:**
1. Create Wizard data models and entities
2. Implement Wizard repository and remote data source
3. Build Wizard BLoC with events and states
4. Design Wizard list screen with cards
5. Implement search functionality
6. Add category and difficulty filters
7. Create Wizard detail screen
8. Implement wizard metadata display (time, difficulty, steps)
9. Add "Start Wizard" action button
10. Implement error handling and loading states

**Deliverables:**
- Wizard browsing interface
- Search and filter functionality
- Wizard detail view
- Navigation to wizard player

---

### Phase 3: Wizard Player - Core Execution (Week 5-7)

**Objectives:**
- Execute wizards step-by-step
- Implement all 12 selection types
- Handle step navigation
- Auto-save progress

**Tasks:**
1. Create WizardRun data models and entities
2. Implement WizardRun repository and remote data source
3. Build WizardRun BLoC with complex state management
4. Design wizard player screen layout
5. Implement step progress indicator
6. Create navigation controls (Next, Previous, Skip)
7. **Build all 12 option set widgets:**
   - Single Select (Radio buttons)
   - Multiple Select (Checkboxes)
   - Text Input (Multi-line)
   - Number Input (Numeric keyboard)
   - Date Input (Date picker)
   - Time Input (Time picker)
   - DateTime Input (Combined picker)
   - Rating (Star rating)
   - Slider (Range slider)
   - Color Picker (Color selection)
   - File Upload (File picker)
   - Rich Text (WYSIWYG editor)
8. Implement conditional dependencies logic
9. Build auto-save mechanism
10. Create step response submission logic
11. Implement option set response submission
12. Handle validation errors
13. Add completion dialog

**Deliverables:**
- Fully functional wizard player
- All 12 input types working
- Auto-save functionality
- Step navigation
- Completion flow

---

### Phase 4: My Runs - Progress Tracking (Week 8-9)

**Objectives:**
- Display user's wizard runs
- Categorize runs (All, In Progress, Completed, Favorites)
- Resume incomplete runs
- Manage favorites

**Tasks:**
1. Create My Runs screen with tab navigation
2. Implement run listing with filtering
3. Build run card widget with status indicators
4. Show progress percentage and dates
5. Add resume functionality for in-progress runs
6. Implement favorite toggle
7. Add delete run with confirmation
8. Create run statistics dashboard
9. Implement pull-to-refresh
10. Add empty state screens

**Deliverables:**
- My Runs interface
- Tab-based filtering
- Resume functionality
- Favorite management
- Statistics display

---

### Phase 5: Store Wizard - Run Repository (Week 10-11)

**Objectives:**
- Display stored wizard runs
- View completed run details
- Share runs
- Export functionality (future)

**Tasks:**
1. Create Store screen layout
2. Implement stored runs listing
3. Build stored run card widget
4. Create run detail view (read-only)
5. Display all user responses
6. Show step-by-step completion data
7. Implement share functionality
8. Create share dialog with permissions
9. Add copy share link to clipboard
10. Implement view-only mode for shared runs
11. Add export placeholder (for future)

**Deliverables:**
- Store interface
- Stored runs listing
- Run detail viewer
- Share functionality
- View-only shared runs

---

### Phase 6: File Uploads & Media (Week 12)

**Objectives:**
- Support file uploads during wizard execution
- Handle image capture from camera
- Display uploaded files

**Tasks:**
1. Implement file picker integration
2. Add image picker (camera/gallery)
3. Create file upload API integration
4. Build file preview widgets
5. Implement upload progress indicator
6. Handle file validation (type, size)
7. Display uploaded files in run details
8. Implement file deletion

**Deliverables:**
- File upload functionality
- Image capture support
- File management in runs

---

### Phase 7: Offline Support & Caching (Week 13)

**Objectives:**
- Cache wizards for offline access
- Store run data locally
- Sync when online

**Tasks:**
1. Set up Hive local database
2. Create local data models
3. Implement wizard caching
4. Cache published wizards on first load
5. Store run responses locally
6. Implement connectivity check
7. Build sync mechanism
8. Show offline indicator
9. Queue actions for when online
10. Handle conflicts

**Deliverables:**
- Offline wizard access
- Local run data storage
- Auto-sync functionality
- Offline mode indicator

---

### Phase 8: Polish & Optimization (Week 14-15)

**Objectives:**
- Improve UI/UX
- Optimize performance
- Add animations
- Handle edge cases

**Tasks:**
1. Add page transitions and animations
2. Implement shimmer loading states
3. Optimize image loading with caching
4. Improve error messages
5. Add haptic feedback
6. Implement dark mode
7. Optimize API calls
8. Add analytics tracking
9. Improve accessibility
10. Handle network timeouts gracefully
11. Add tooltips and help text
12. Implement rate limiting
13. Optimize battery usage

**Deliverables:**
- Polished UI with animations
- Performance optimizations
- Improved error handling
- Dark mode support

---

### Phase 9: Testing (Week 16-17)

**Objectives:**
- Write comprehensive tests
- Ensure reliability
- Fix bugs

**Tasks:**
1. Write unit tests for all BLoCs
2. Write unit tests for repositories
3. Write unit tests for use cases
4. Create widget tests for key screens
5. Write integration tests for critical flows
6. Test all 12 option set widgets
7. Test file upload functionality
8. Test offline mode
9. Test authentication flows
10. Perform user acceptance testing
11. Fix identified bugs
12. Conduct performance testing

**Deliverables:**
- 80%+ test coverage
- Integration test suite
- Bug fixes
- Performance report

---

### Phase 10: Deployment (Week 18)

**Objectives:**
- Prepare for release
- Deploy to stores
- Set up monitoring

**Tasks:**
1. Configure app signing (Android)
2. Configure provisioning profiles (iOS)
3. Set up CI/CD pipeline
4. Create app icons and splash screens
5. Write app store descriptions
6. Take screenshots for stores
7. Build release APK/IPA
8. Test release builds
9. Submit to Google Play Store
10. Submit to Apple App Store
11. Set up crash reporting (Firebase Crashlytics)
12. Set up analytics
13. Create user documentation
14. Plan post-launch support

**Deliverables:**
- Published Android app
- Published iOS app
- Monitoring setup
- Documentation

---

## 7. Feature Specifications

### 7.1 Run Wizard Feature

**User Flow:**
1. User browses published wizards
2. User selects a wizard to run
3. App creates a new wizard run via API
4. User completes wizard step-by-step
5. Responses are auto-saved every 30 seconds
6. User can navigate back/forward through steps
7. User completes final step
8. Completion dialog appears with save options
9. Run is marked as completed and stored (if selected)

**Key Components:**

#### Wizard Player Screen
```dart
class WizardPlayerScreen extends StatefulWidget {
  final String wizardId;

  @override
  State<WizardPlayerScreen> createState() => _WizardPlayerScreenState();
}

class _WizardPlayerScreenState extends State<WizardPlayerScreen> {
  late PageController _pageController;
  int _currentStepIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Wizard Name'),
        actions: [
          IconButton(
            icon: Icon(Icons.close),
            onPressed: () => _showExitDialog(),
          ),
        ],
      ),
      body: BlocBuilder<WizardRunBloc, WizardRunState>(
        builder: (context, state) {
          if (state is WizardRunLoaded) {
            return Column(
              children: [
                // Progress indicator
                LinearProgressIndicator(
                  value: state.progressPercentage / 100,
                ),
                // Step indicator
                StepProgressIndicator(
                  currentStep: _currentStepIndex + 1,
                  totalSteps: state.wizard.steps.length,
                ),
                // Step content
                Expanded(
                  child: PageView.builder(
                    controller: _pageController,
                    itemCount: state.wizard.steps.length,
                    onPageChanged: (index) {
                      setState(() => _currentStepIndex = index);
                    },
                    itemBuilder: (context, index) {
                      return StepContent(
                        step: state.wizard.steps[index],
                        responses: state.responses,
                        onResponseChanged: (optionSetId, value) {
                          // Save response
                        },
                      );
                    },
                  ),
                ),
                // Navigation buttons
                WizardNavigation(
                  currentStep: _currentStepIndex,
                  totalSteps: state.wizard.steps.length,
                  onNext: _handleNext,
                  onPrevious: _handlePrevious,
                  onComplete: _handleComplete,
                ),
              ],
            );
          }
          return LoadingIndicator();
        },
      ),
    );
  }
}
```

#### Option Set Rendering
Each of the 12 selection types has its own widget:

**Example: Single Select Widget**
```dart
class SingleSelectWidget extends StatelessWidget {
  final OptionSet optionSet;
  final String? selectedValue;
  final Function(String) onChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          optionSet.name,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        if (optionSet.description != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(optionSet.description!),
          ),
        ...optionSet.options.map((option) {
          return RadioListTile<String>(
            title: Text(option.label),
            subtitle: option.description != null
                ? Text(option.description!)
                : null,
            value: option.value,
            groupValue: selectedValue,
            onChanged: (value) {
              if (value != null) {
                onChanged(value);
              }
            },
          );
        }).toList(),
      ],
    );
  }
}
```

**Example: File Upload Widget**
```dart
class FileUploadWidget extends StatefulWidget {
  final OptionSet optionSet;
  final Function(File) onFileSelected;

  @override
  State<FileUploadWidget> createState() => _FileUploadWidgetState();
}

class _FileUploadWidgetState extends State<FileUploadWidget> {
  File? _selectedFile;
  bool _isUploading = false;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles();
    if (result != null) {
      setState(() {
        _selectedFile = File(result.files.single.path!);
      });
      await _uploadFile();
    }
  }

  Future<void> _uploadFile() async {
    setState(() => _isUploading = true);
    try {
      await widget.onFileSelected(_selectedFile!);
    } finally {
      setState(() => _isUploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(widget.optionSet.name),
        ElevatedButton.icon(
          onPressed: _isUploading ? null : _pickFile,
          icon: Icon(Icons.upload_file),
          label: Text('Select File'),
        ),
        if (_selectedFile != null)
          Chip(
            avatar: Icon(Icons.attach_file),
            label: Text(path.basename(_selectedFile!.path)),
            onDeleted: () {
              setState(() => _selectedFile = null);
            },
          ),
        if (_isUploading)
          CircularProgressIndicator(),
      ],
    );
  }
}
```

#### Auto-Save Mechanism
```dart
class AutoSaveService {
  Timer? _timer;
  final WizardRunRepository _repository;

  void startAutoSave({
    required String runId,
    required int currentStepIndex,
    required Map<String, dynamic> responses,
  }) {
    _timer?.cancel();
    _timer = Timer.periodic(
      const Duration(seconds: 30),
      (_) async {
        await _repository.updateRunProgress(
          runId: runId,
          currentStepIndex: currentStepIndex,
        );
        // Save current responses
        await _saveResponses(runId, responses);
      },
    );
  }

  void stopAutoSave() {
    _timer?.cancel();
  }

  Future<void> _saveResponses(
    String runId,
    Map<String, dynamic> responses,
  ) async {
    // Implementation to save responses
  }
}
```

---

### 7.2 Store Wizard Feature

**User Flow:**
1. User navigates to Store screen
2. App loads stored wizard runs via API
3. User browses stored runs
4. User taps on a run to view details
5. App displays read-only view of all responses
6. User can share run with others
7. User can export run data (future feature)

**Key Components:**

#### Store Screen
```dart
class StoreScreen extends StatefulWidget {
  @override
  State<StoreScreen> createState() => _StoreScreenState();
}

class _StoreScreenState extends State<StoreScreen> {
  @override
  void initState() {
    super.initState();
    context.read<StoreBloc>().add(LoadStoredRuns());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Store'),
        actions: [
          IconButton(
            icon: Icon(Icons.search),
            onPressed: () => _showSearchDialog(),
          ),
        ],
      ),
      body: BlocBuilder<StoreBloc, StoreState>(
        builder: (context, state) {
          if (state is StoreLoading) {
            return Center(child: CircularProgressIndicator());
          }

          if (state is StoreLoaded) {
            if (state.storedRuns.isEmpty) {
              return EmptyStateWidget(
                icon: Icons.inventory_2_outlined,
                title: 'No Stored Runs',
                message: 'Complete a wizard and save it to see it here',
              );
            }

            return RefreshIndicator(
              onRefresh: () async {
                context.read<StoreBloc>().add(LoadStoredRuns());
              },
              child: ListView.builder(
                padding: EdgeInsets.all(16),
                itemCount: state.storedRuns.length,
                itemBuilder: (context, index) {
                  final run = state.storedRuns[index];
                  return StoredRunCard(
                    run: run,
                    onTap: () => _navigateToRunDetail(run.id),
                    onShare: () => _showShareDialog(run),
                  );
                },
              ),
            );
          }

          if (state is StoreError) {
            return ErrorWidget(
              message: state.message,
              onRetry: () {
                context.read<StoreBloc>().add(LoadStoredRuns());
              },
            );
          }

          return SizedBox.shrink();
        },
      ),
    );
  }
}
```

#### Stored Run Card
```dart
class StoredRunCard extends StatelessWidget {
  final WizardRun run;
  final VoidCallback onTap;
  final VoidCallback onShare;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      run.runName ?? 'Unnamed Run',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ),
                  Chip(
                    label: Text('Stored'),
                    backgroundColor: Colors.green.shade100,
                  ),
                ],
              ),
              SizedBox(height: 8),
              if (run.runDescription != null)
                Text(
                  run.runDescription!,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.calendar_today, size: 16),
                  SizedBox(width: 4),
                  Text(
                    'Completed: ${_formatDate(run.completedAt)}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
              SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: run.tags.map((tag) {
                  return Chip(
                    label: Text(tag),
                    visualDensity: VisualDensity.compact,
                  );
                }).toList(),
              ),
              SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton.icon(
                    onPressed: onShare,
                    icon: Icon(Icons.share),
                    label: Text('Share'),
                  ),
                  SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: onTap,
                    child: Text('View'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime? date) {
    if (date == null) return 'N/A';
    return DateFormat('MMM dd, yyyy').format(date);
  }
}
```

#### Run Detail Viewer (Read-Only)
```dart
class StoredRunDetailScreen extends StatelessWidget {
  final String runId;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Run Details'),
        actions: [
          IconButton(
            icon: Icon(Icons.share),
            onPressed: () => _showShareDialog(context),
          ),
          IconButton(
            icon: Icon(Icons.download),
            onPressed: () => _showExportDialog(context),
          ),
        ],
      ),
      body: BlocBuilder<StoreBloc, StoreState>(
        builder: (context, state) {
          if (state is RunDetailLoaded) {
            return SingleChildScrollView(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Run metadata
                  _buildRunMetadata(state.runDetail),
                  Divider(height: 32),
                  // Steps with responses
                  ...state.runDetail.stepResponses.map((stepResponse) {
                    return _buildStepSection(
                      stepResponse,
                      state.runDetail.optionSetResponses,
                    );
                  }).toList(),
                ],
              ),
            );
          }
          return Center(child: CircularProgressIndicator());
        },
      ),
    );
  }

  Widget _buildStepSection(
    StepResponse stepResponse,
    List<OptionSetResponse> optionSetResponses,
  ) {
    final stepOptionSets = optionSetResponses
        .where((osr) => osr.stepResponseId == stepResponse.id)
        .toList();

    return Card(
      margin: EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              stepResponse.stepName,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 16),
            ...stepOptionSets.map((optionSet) {
              return _buildOptionSetResponse(optionSet);
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildOptionSetResponse(OptionSetResponse optionSet) {
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            optionSet.optionSetName ?? 'Question',
            style: TextStyle(fontWeight: FontWeight.w500),
          ),
          SizedBox(height: 4),
          Text(
            _formatResponseValue(optionSet),
            style: TextStyle(color: Colors.grey[700]),
          ),
        ],
      ),
    );
  }

  String _formatResponseValue(OptionSetResponse optionSet) {
    // Format based on selection type
    switch (optionSet.selectionType) {
      case 'text_input':
      case 'number_input':
        return optionSet.responseValue['value']?.toString() ?? 'N/A';
      case 'date_input':
        final dateStr = optionSet.responseValue['value'];
        if (dateStr != null) {
          final date = DateTime.parse(dateStr);
          return DateFormat('MMM dd, yyyy').format(date);
        }
        return 'N/A';
      case 'rating':
        final rating = optionSet.responseValue['value'];
        return '⭐ $rating / 5';
      case 'file_upload':
        return 'File uploaded: ${optionSet.responseValue['fileName']}';
      default:
        return optionSet.responseValue['value']?.toString() ?? 'N/A';
    }
  }
}
```

---

### 7.3 My Runs Feature

**User Flow:**
1. User navigates to My Runs screen
2. App displays tabs: All, In Progress, Completed, Favorites
3. User switches between tabs to filter runs
4. User can resume in-progress runs
5. User can mark/unmark runs as favorites
6. User can delete runs with confirmation

**Key Components:**

#### My Runs Screen with Tabs
```dart
class MyRunsScreen extends StatefulWidget {
  @override
  State<MyRunsScreen> createState() => _MyRunsScreenState();
}

class _MyRunsScreenState extends State<MyRunsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    context.read<WizardRunBloc>().add(LoadUserRuns());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('My Runs'),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: 'All'),
            Tab(text: 'In Progress'),
            Tab(text: 'Completed'),
            Tab(text: 'Favorites'),
          ],
        ),
      ),
      body: BlocBuilder<WizardRunBloc, WizardRunState>(
        builder: (context, state) {
          if (state is RunsLoaded) {
            return Column(
              children: [
                // Statistics
                _buildStatsBar(state.stats),
                // Tab content
                Expanded(
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildRunList(state.allRuns),
                      _buildRunList(state.inProgressRuns),
                      _buildRunList(state.completedRuns),
                      _buildRunList(state.favoriteRuns),
                    ],
                  ),
                ),
              ],
            );
          }
          return Center(child: CircularProgressIndicator());
        },
      ),
    );
  }

  Widget _buildStatsBar(WizardRunStats stats) {
    return Container(
      padding: EdgeInsets.all(16),
      color: Colors.grey[100],
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem('Total', stats.totalRuns),
          _buildStatItem('In Progress', stats.inProgressRuns),
          _buildStatItem('Completed', stats.completedRuns),
          _buildStatItem('Favorites', stats.favoriteRuns),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, int value) {
    return Column(
      children: [
        Text(
          value.toString(),
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildRunList(List<WizardRun> runs) {
    if (runs.isEmpty) {
      return EmptyStateWidget(
        icon: Icons.assignment_outlined,
        title: 'No Runs',
        message: 'Start a wizard to see it here',
      );
    }

    return ListView.builder(
      padding: EdgeInsets.all(16),
      itemCount: runs.length,
      itemBuilder: (context, index) {
        final run = runs[index];
        return RunCard(
          run: run,
          onTap: () {
            if (run.status == 'in_progress') {
              _resumeRun(run);
            } else {
              _viewRun(run);
            }
          },
          onFavoriteToggle: () {
            context.read<WizardRunBloc>().add(
              ToggleFavorite(runId: run.id),
            );
          },
          onDelete: () => _showDeleteConfirmation(run),
        );
      },
    );
  }
}
```

---

## 8. UI/UX Design Guidelines

### Design System

#### Color Palette
```dart
class AppColors {
  // Primary colors
  static const primary = Color(0xFF6200EE);
  static const primaryVariant = Color(0xFF3700B3);
  static const secondary = Color(0xFF03DAC6);
  static const secondaryVariant = Color(0xFF018786);

  // Status colors
  static const success = Color(0xFF4CAF50);
  static const warning = Color(0xFFFFC107);
  static const error = Color(0xFFF44336);
  static const info = Color(0xFF2196F3);

  // Run status colors
  static const inProgress = Color(0xFF2196F3);
  static const completed = Color(0xFF4CAF50);
  static const abandoned = Color(0xFF9E9E9E);

  // Neutral colors
  static const background = Color(0xFFF5F5F5);
  static const surface = Color(0xFFFFFFFF);
  static const textPrimary = Color(0xFF212121);
  static const textSecondary = Color(0xFF757575);
  static const divider = Color(0xFFBDBDBD);
}
```

#### Typography
```dart
class AppTextStyles {
  static const headline1 = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.bold,
    color: AppColors.textPrimary,
  );

  static const headline2 = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: AppColors.textPrimary,
  );

  static const subtitle1 = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w500,
    color: AppColors.textPrimary,
  );

  static const body1 = TextStyle(
    fontSize: 14,
    color: AppColors.textPrimary,
  );

  static const caption = TextStyle(
    fontSize: 12,
    color: AppColors.textSecondary,
  );
}
```

#### Spacing
```dart
class AppSpacing {
  static const xs = 4.0;
  static const sm = 8.0;
  static const md = 16.0;
  static const lg = 24.0;
  static const xl = 32.0;
}
```

### Screen Layouts

#### Bottom Navigation
```dart
class HomeScreen extends StatefulWidget {
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final _screens = [
    DashboardScreen(),
    WizardListScreen(),
    MyRunsScreen(),
    StoreScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.auto_awesome),
            label: 'Wizards',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.assignment),
            label: 'My Runs',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.inventory_2),
            label: 'Store',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
```

---

## 9. Security Considerations

### Authentication Security

1. **JWT Token Storage**
   - Store access tokens in `flutter_secure_storage`
   - Never store tokens in shared preferences
   - Implement token refresh mechanism

2. **HTTPS Only**
   - All API calls must use HTTPS in production
   - Implement SSL pinning for added security

3. **Input Validation**
   - Validate all user inputs on frontend
   - Sanitize data before sending to API
   - Handle SQL injection prevention (backend responsibility)

4. **File Upload Security**
   - Validate file types before upload
   - Limit file sizes
   - Scan for malware (backend responsibility)

5. **Secure Data Transmission**
   - Use encrypted connections
   - Implement request signing for sensitive operations

### Code Security

```dart
// lib/core/security/security_service.dart
class SecurityService {
  final FlutterSecureStorage _secureStorage;

  SecurityService(this._secureStorage);

  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: 'access_token', value: token);
  }

  Future<String?> getToken() async {
    return await _secureStorage.read(key: 'access_token');
  }

  Future<void> deleteToken() async {
    await _secureStorage.delete(key: 'access_token');
  }

  // Implement SSL pinning
  Future<SecurityContext> getSecurityContext() async {
    final context = SecurityContext(withTrustedRoots: false);
    // Load certificate
    final certBytes = await rootBundle.load('assets/cert.pem');
    context.setTrustedCertificatesBytes(certBytes.buffer.asUint8List());
    return context;
  }
}
```

---

## 10. Testing Strategy

### Unit Tests
- Test all BLoCs (events → states)
- Test repositories (mock data sources)
- Test use cases
- Test models (serialization/deserialization)

### Widget Tests
- Test individual widgets
- Test user interactions
- Test state changes

### Integration Tests
```dart
// integration_test/wizard_run_flow_test.dart
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Wizard Run Flow', () {
    testWidgets('Complete wizard run end-to-end', (tester) async {
      // Launch app
      await tester.pumpWidget(MyApp());

      // Login
      await tester.enterText(
        find.byKey(Key('username_field')),
        'testuser',
      );
      await tester.enterText(
        find.byKey(Key('password_field')),
        'password123',
      );
      await tester.tap(find.byKey(Key('login_button')));
      await tester.pumpAndSettle();

      // Navigate to wizards
      await tester.tap(find.text('Wizards'));
      await tester.pumpAndSettle();

      // Select first wizard
      await tester.tap(find.byType(WizardCard).first);
      await tester.pumpAndSettle();

      // Start wizard
      await tester.tap(find.text('Start Wizard'));
      await tester.pumpAndSettle();

      // Complete first step
      await tester.tap(find.byType(RadioListTile).first);
      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();

      // Verify progress
      expect(find.text('Step 2'), findsOneWidget);
    });
  });
}
```

---

## 11. Deployment Plan

### Android Deployment

1. **Configure Signing**
   ```gradle
   // android/app/build.gradle
   android {
       signingConfigs {
           release {
               keyAlias keystoreProperties['keyAlias']
               keyPassword keystoreProperties['keyPassword']
               storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
               storePassword keystoreProperties['storePassword']
           }
       }
       buildTypes {
           release {
               signingConfig signingConfigs.release
           }
       }
   }
   ```

2. **Build Release APK**
   ```bash
   flutter build apk --release
   ```

3. **Build App Bundle**
   ```bash
   flutter build appbundle --release
   ```

### iOS Deployment

1. **Configure Xcode**
   - Set up provisioning profiles
   - Configure app signing
   - Set bundle identifier

2. **Build Release**
   ```bash
   flutter build ios --release
   ```

3. **Archive and Upload**
   - Open Xcode
   - Archive app
   - Upload to App Store Connect

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build_android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      - run: flutter pub get
      - run: flutter test
      - run: flutter build apk --release
      - uses: actions/upload-artifact@v3
        with:
          name: release-apk
          path: build/app/outputs/flutter-apk/app-release.apk

  build_ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - run: flutter pub get
      - run: flutter test
      - run: flutter build ios --release --no-codesign
```

---

## 12. Development Timeline

### Timeline Summary (18 Weeks Total)

| Phase | Weeks | Key Deliverables |
|-------|-------|------------------|
| Phase 1: Foundation & Auth | 1-2 | Authentication, base UI |
| Phase 2: Wizard Listing | 3-4 | Wizard browsing |
| Phase 3: Wizard Player | 5-7 | Full wizard execution |
| Phase 4: My Runs | 8-9 | Run tracking |
| Phase 5: Store | 10-11 | Run repository |
| Phase 6: File Uploads | 12 | Media handling |
| Phase 7: Offline Support | 13 | Caching & sync |
| Phase 8: Polish | 14-15 | UI/UX improvements |
| Phase 9: Testing | 16-17 | Comprehensive testing |
| Phase 10: Deployment | 18 | App store release |

### Milestones

- **Week 2**: Authentication working
- **Week 4**: Wizard listing functional
- **Week 7**: Wizard execution complete
- **Week 11**: All core features done
- **Week 15**: Polished app ready
- **Week 18**: Published to stores

---

## Appendix

### A. Required Backend Updates

The existing backend is already 100% ready for the mobile app. No changes needed! The following endpoints are available:

#### Authentication Endpoints
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`

#### Wizard Endpoints
- `GET /api/v1/wizards` (List published wizards)
- `GET /api/v1/wizards/{id}` (Get wizard details)

#### Wizard Run Endpoints
- `POST /api/v1/wizard-runs` (Create run)
- `GET /api/v1/wizard-runs/{id}` (Get run details)
- `GET /api/v1/wizard-runs/in-progress`
- `GET /api/v1/wizard-runs/completed`
- `GET /api/v1/wizard-runs/stored`
- `GET /api/v1/wizard-runs/favorites`
- `GET /api/v1/wizard-runs/stats`
- `POST /api/v1/wizard-runs/{id}/complete`
- `POST /api/v1/wizard-runs/{id}/progress`
- `PUT /api/v1/wizard-runs/{id}`
- `DELETE /api/v1/wizard-runs/{id}`

#### Step Response Endpoints
- `POST /api/v1/wizard-runs/{runId}/steps`
- `PUT /api/v1/wizard-runs/steps/{stepResponseId}`

#### Option Set Response Endpoints
- `POST /api/v1/wizard-runs/{runId}/option-sets`
- `PUT /api/v1/wizard-runs/option-sets/{responseId}`

#### File Upload Endpoints
- `POST /api/v1/wizard-runs/{runId}/upload`

#### Share Endpoints
- `POST /api/v1/wizard-runs/{runId}/share`
- `GET /api/v1/wizard-runs/share/{shareToken}`

### B. Environment Configuration

**Backend URL Configuration:**
- Development: `http://localhost:8000/api/v1`
- Staging: `https://staging-api.yourapp.com/api/v1`
- Production: `https://api.yourapp.com/api/v1`

**Update in `lib/core/constants/api_constants.dart`**

### C. Sample API Responses

**Login Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }
}
```

**Wizard Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Business Plan Wizard",
  "description": "Create a comprehensive business plan",
  "difficulty_level": "medium",
  "estimated_time": 30,
  "is_published": true,
  "steps": [
    {
      "id": "step-uuid",
      "name": "Company Overview",
      "step_order": 1,
      "option_sets": [
        {
          "id": "optionset-uuid",
          "name": "Company Name",
          "selection_type": "text_input",
          "is_required": true,
          "display_order": 1
        }
      ]
    }
  ]
}
```

---

## Conclusion

This implementation plan provides a comprehensive roadmap for developing a Flutter mobile app that integrates seamlessly with your existing Multi-Wizard Platform backend. The 18-week timeline is realistic and accounts for all features, testing, and deployment.

**Key Success Factors:**
1. Clean architecture ensures maintainability
2. BLoC pattern provides robust state management
3. Comprehensive testing guarantees reliability
4. Offline support enables better UX
5. Existing backend APIs are ready to use

**Next Steps:**
1. Review and approve this plan
2. Set up Flutter development environment
3. Begin Phase 1: Foundation & Authentication
4. Establish regular sprint reviews
5. Monitor progress against timeline

The mobile app will enable users to run wizards and manage stored runs on-the-go, expanding the reach of your Multi-Wizard Platform significantly.
