-- Clean Database Script for Student Management System
-- This script creates the core database structure without redundant Marten document store components

-- Migration history table (keep for EF Core)
CREATE TABLE "__EFMigrationsHistory"
(
    "MigrationId"    VARCHAR(150) NOT NULL
        CONSTRAINT "PK___EFMigrationsHistory" PRIMARY KEY,
    "ProductVersion" VARCHAR(32)  NOT NULL
);

-- Core academic structure
CREATE TABLE "Courses"
(
    "Id"          UUID                     NOT NULL
        CONSTRAINT "PK_Courses" PRIMARY KEY,
    "Code"        VARCHAR(20)              NOT NULL,
    "Name"        VARCHAR(100)             NOT NULL,
    "Description" VARCHAR(500)             NOT NULL,
    "CreatedAt"   TIMESTAMP WITH TIME ZONE NOT NULL,
    "UpdatedAt"   TIMESTAMP WITH TIME ZONE NOT NULL,
    "IsDeleted"   BOOLEAN DEFAULT FALSE    NOT NULL
);

CREATE UNIQUE INDEX "IX_Courses_Code" ON "Courses" ("Code");

CREATE TABLE "Rooms"
(
    "Id"        UUID                                               NOT NULL
        CONSTRAINT "PK_Rooms" PRIMARY KEY,
    "RoomName"  VARCHAR(50)                                        NOT NULL,
    "Building"  VARCHAR(50)                                        NOT NULL,
    "CreatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "IsDeleted" BOOLEAN                                            NOT NULL
);

CREATE INDEX "IX_Rooms_Building" ON "Rooms" ("Building");
CREATE UNIQUE INDEX "IX_Rooms_RoomName" ON "Rooms" ("RoomName");

CREATE TABLE "ClassSections"
(
    "Id"          UUID                                               NOT NULL
        CONSTRAINT "PK_ClassSections" PRIMARY KEY,
    "CourseId"    UUID                                               NOT NULL
        CONSTRAINT "FK_ClassSections_Courses_CourseId"
            REFERENCES "Courses" ON DELETE RESTRICT,
    "LecturerId"  UUID,
    "SectionCode" VARCHAR(50)                                        NOT NULL,
    "Semester"    VARCHAR(20)                                        NOT NULL,
    "CreatedAt"   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "IsDeleted"   BOOLEAN                                            NOT NULL
);

CREATE INDEX "IX_ClassSections_CourseId" ON "ClassSections" ("CourseId");
CREATE INDEX "IX_ClassSections_LecturerId" ON "ClassSections" ("LecturerId");
CREATE UNIQUE INDEX "IX_ClassSections_SectionCode" ON "ClassSections" ("SectionCode");
CREATE INDEX "IX_ClassSections_Semester" ON "ClassSections" ("Semester");

CREATE TABLE "Enrollments"
(
    "Id"             UUID                                               NOT NULL
        CONSTRAINT "PK_Enrollments" PRIMARY KEY,
    "StudentId"      UUID                                               NOT NULL,
    "ClassSectionId" UUID                                               NOT NULL
        CONSTRAINT "FK_Enrollments_ClassSections_ClassSectionId"
            REFERENCES "ClassSections" ON DELETE RESTRICT,
    "EnrolledAt"     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "Status"         VARCHAR(20)                                        NOT NULL
);

CREATE INDEX "IX_Enrollments_ClassSectionId" ON "Enrollments" ("ClassSectionId");
CREATE INDEX "IX_Enrollments_StudentId" ON "Enrollments" ("StudentId");
CREATE UNIQUE INDEX "IX_Enrollments_StudentId_ClassSectionId" ON "Enrollments" ("StudentId", "ClassSectionId");

CREATE TABLE "Schedules"
(
    "Id"             UUID                                               NOT NULL
        CONSTRAINT "PK_Schedules" PRIMARY KEY,
    "ClassSectionId" UUID                                               NOT NULL
        CONSTRAINT "FK_Schedules_ClassSections_ClassSectionId"
            REFERENCES "ClassSections" ON DELETE RESTRICT,
    "RoomId"         UUID                                               NOT NULL
        CONSTRAINT "FK_Schedules_Rooms_RoomId"
            REFERENCES "Rooms" ON DELETE RESTRICT,
    "StartDate"      DATE                                               NOT NULL,
    "EndDate"        DATE                                               NOT NULL,
    "StartTime"      TIME                                               NOT NULL,
    "EndTime"        TIME                                               NOT NULL,
    "WeekDay"        VARCHAR(20)                                        NOT NULL,
    "IsDeleted"      BOOLEAN                                            NOT NULL,
    "CreatedAt"      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT "CK_Schedules_EndTime_After_StartTime" CHECK ("EndTime" > "StartTime")
);

CREATE INDEX "IX_Schedules_ClassSectionId" ON "Schedules" ("ClassSectionId");
CREATE INDEX "IX_Schedules_RoomId" ON "Schedules" ("RoomId");
CREATE INDEX "IX_Schedules_StartDate" ON "Schedules" ("StartDate");
CREATE INDEX "IX_Schedules_EndDate" ON "Schedules" ("EndDate");
CREATE INDEX "IX_Schedules_StartTime" ON "Schedules" ("StartTime");
CREATE INDEX "IX_Schedules_EndTime" ON "Schedules" ("EndTime");
CREATE INDEX "IX_Schedules_WeekDay" ON "Schedules" ("WeekDay");
CREATE INDEX "IX_Schedules_RoomId_StartDate_StartTime_EndTime" ON "Schedules" ("RoomId", "StartDate", "StartTime", "EndTime");

-- User management and authentication
CREATE TABLE "Accounts"
(
    "Id"                   UUID                                               NOT NULL
        CONSTRAINT "PK_Accounts" PRIMARY KEY,
    "Email"                VARCHAR(255)                                       NOT NULL,
    "PasswordHash"         VARCHAR(255)                                       NOT NULL,
    "PasswordSalt"         VARCHAR(255)                                       NOT NULL,
    "Role"                 VARCHAR(50)                                        NOT NULL,
    "ResetToken"           VARCHAR(255),
    "Status"               TEXT                     DEFAULT 'Active'::TEXT    NOT NULL,
    "ResetTokenExpiryTime" TIMESTAMP WITH TIME ZONE,
    "CreatedAt"            TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"            TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX "IX_Accounts_Email" ON "Accounts" ("Email");
CREATE UNIQUE INDEX "IX_Accounts_ResetToken" ON "Accounts" ("ResetToken") WHERE ("ResetToken" IS NOT NULL);
CREATE INDEX "IX_Accounts_Status" ON "Accounts" ("Status");

CREATE TABLE "Users"
(
    "Id"                UUID                                               NOT NULL
        CONSTRAINT "PK_Users" PRIMARY KEY,
    "AccountId"         UUID                                               NOT NULL
        CONSTRAINT "FK_Users_Accounts_AccountId"
            REFERENCES "Accounts" ON DELETE CASCADE,
    "FullName"          VARCHAR(255)                                       NOT NULL,
    "PhoneNumber"       VARCHAR(20),
    "CreatedAt"         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "HasFaceId"         BOOLEAN                  DEFAULT FALSE             NOT NULL,
    "FaceIdLastUpdated" TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX "IX_Users_AccountId" ON "Users" ("AccountId");
CREATE INDEX "IX_Users_FullName" ON "Users" ("FullName");
CREATE INDEX "IX_Users_PhoneNumber" ON "Users" ("PhoneNumber");

-- Device management
CREATE TABLE "Devices"
(
    "Id"                    UUID                                               NOT NULL
        CONSTRAINT "PK_Devices" PRIMARY KEY,
    "UserId"                UUID                                               NOT NULL,
    "DeviceName"            VARCHAR(255)                                       NOT NULL,
    "DeviceToken"           VARCHAR(255)                                       NOT NULL,
    "AndroidId"             VARCHAR(255)                                       NOT NULL,
    "Platform"              VARCHAR(50),
    "OsVersion"             VARCHAR(50),
    "Model"                 VARCHAR(100),
    "Manufacturer"          VARCHAR(100),
    "AppVersion"            VARCHAR(50),
    "PushNotificationToken" VARCHAR(500),
    "CreatedAt"             TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"             TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "LastVerifiedAt"        TIMESTAMP WITH TIME ZONE,
    "Status"                TEXT                     DEFAULT 'Active'::TEXT    NOT NULL
);

CREATE UNIQUE INDEX "IX_Devices_AndroidId" ON "Devices" ("AndroidId");
CREATE UNIQUE INDEX "IX_Devices_DeviceToken" ON "Devices" ("DeviceToken");
CREATE INDEX "IX_Devices_UserId" ON "Devices" ("UserId");
CREATE INDEX "IX_Devices_Status" ON "Devices" ("Status");
CREATE INDEX "IX_Devices_AndroidId_Status" ON "Devices" ("AndroidId", "Status");
CREATE INDEX "IX_Devices_UserId_AndroidId" ON "Devices" ("UserId", "AndroidId");

-- Session and attendance management
CREATE TABLE "Sessions"
(
    "Id"             UUID                                               NOT NULL
        CONSTRAINT "PK_Sessions" PRIMARY KEY,
    "ScheduleId"     UUID                                               NOT NULL,
    "LecturerId"     UUID,
    "StartTime"      TIMESTAMP WITH TIME ZONE                           NOT NULL,
    "EndTime"        TIMESTAMP WITH TIME ZONE                           NOT NULL,
    "Status"         VARCHAR(20)                                        NOT NULL,
    "SessionNumber"  INTEGER                                            NOT NULL,
    "CreatedAt"      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"      TIMESTAMP WITH TIME ZONE,
    "ActualEndTime"  TIMESTAMP WITH TIME ZONE,
    "SessionConfigs" JSONB                                              NOT NULL,
    CONSTRAINT "CK_Sessions_EndTime_After_StartTime" CHECK ("EndTime" > "StartTime")
);

CREATE INDEX "IX_Sessions_ScheduleId" ON "Sessions" ("ScheduleId");
CREATE INDEX "IX_Sessions_LecturerId" ON "Sessions" ("LecturerId");
CREATE INDEX "IX_Sessions_StartTime" ON "Sessions" ("StartTime");
CREATE INDEX "IX_Sessions_SessionNumber" ON "Sessions" ("SessionNumber");

CREATE TABLE "Rounds"
(
    "Id"          UUID                                               NOT NULL
        CONSTRAINT "PK_Rounds" PRIMARY KEY,
    "SessionId"   UUID                                               NOT NULL
        CONSTRAINT "FK_Rounds_Sessions_SessionId"
            REFERENCES "Sessions" ON DELETE CASCADE,
    "RoundNumber" INTEGER                                            NOT NULL,
    "StartTime"   TIMESTAMP WITH TIME ZONE                           NOT NULL,
    "EndTime"     TIMESTAMP WITH TIME ZONE                           NOT NULL,
    "Status"      VARCHAR(20)                                        NOT NULL,
    "CreatedAt"   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "CK_Rounds_EndTime_After_StartTime" CHECK ("EndTime" > "StartTime")
);

CREATE INDEX "IX_Rounds_SessionId" ON "Rounds" ("SessionId");
CREATE UNIQUE INDEX "IX_Rounds_SessionId_RoundNumber" ON "Rounds" ("SessionId", "RoundNumber");
CREATE INDEX "IX_Rounds_StartTime" ON "Rounds" ("StartTime");
CREATE INDEX "IX_Rounds_EndTime" ON "Rounds" ("EndTime");

CREATE TABLE "AttendanceRecords"
(
    "Id"                 UUID                                               NOT NULL
        CONSTRAINT "PK_AttendanceRecords" PRIMARY KEY,
    "StudentId"          UUID                                               NOT NULL,
    "SessionId"          UUID                                               NOT NULL
        CONSTRAINT "FK_AttendanceRecords_Sessions_SessionId"
            REFERENCES "Sessions" ON DELETE CASCADE,
    "Status"             TEXT                                               NOT NULL,
    "IsManual"           BOOLEAN                                            NOT NULL,
    "CreatedAt"          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "ExpiredAt"          TIMESTAMP WITH TIME ZONE                           NOT NULL,
    "UpdatedAt"          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "PercentageAttended" DOUBLE PRECISION                                   NOT NULL,
    "FaceIdStatus"       TEXT
);

CREATE INDEX "IX_AttendanceRecords_SessionId" ON "AttendanceRecords" ("SessionId");
CREATE INDEX "IX_AttendanceRecords_StudentId" ON "AttendanceRecords" ("StudentId");
CREATE INDEX "IX_AttendanceRecords_Status" ON "AttendanceRecords" ("Status");

-- Face recognition system
CREATE TABLE "FaceEmbeddings"
(
    "Id"                 UUID                                               NOT NULL
        CONSTRAINT "PK_FaceEmbeddings" PRIMARY KEY,
    "UserId"             UUID                                               NOT NULL,
    "EncryptedEmbedding" BYTEA                                              NOT NULL,
    "CreatedAt"          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX "IX_FaceEmbeddings_UserId" ON "FaceEmbeddings" ("UserId");

CREATE TABLE "FaceIdVerifyRequests"
(
    "Id"              UUID                                               NOT NULL
        CONSTRAINT "PK_FaceIdVerifyRequests" PRIMARY KEY,
    "RequestGroupId"  UUID                                               NOT NULL,
    "TargetUserId"    UUID                                               NOT NULL,
    "InitiatorUserId" UUID,
    "SessionId"       UUID,
    "ClassSectionId"  UUID,
    "Threshold"       REAL                     DEFAULT 0.7               NOT NULL,
    "Status"          INTEGER                                            NOT NULL,
    "CreatedAt"       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "ExpiresAt"       TIMESTAMP WITH TIME ZONE                           NOT NULL,
    "CompletedAt"     TIMESTAMP WITH TIME ZONE,
    "Matched"         BOOLEAN,
    "Similarity"      REAL,
    "NotificationId"  VARCHAR(128),
    "MetadataJson"    JSONB
);

CREATE INDEX "IX_FaceIdReq_ExpiresAt" ON "FaceIdVerifyRequests" ("ExpiresAt");
CREATE INDEX "IX_FaceIdReq_Group_Target_Status_Exp" ON "FaceIdVerifyRequests" ("RequestGroupId", "TargetUserId", "Status", "ExpiresAt");
CREATE INDEX "IX_FaceIdReq_Session_Status" ON "FaceIdVerifyRequests" ("SessionId", "Status");

-- Configuration and settings system
CREATE TABLE "AttributeDefinitions"
(
    "Id"                UUID                                               NOT NULL
        CONSTRAINT "PK_AttributeDefinitions" PRIMARY KEY,
    "Key"               VARCHAR(100)                                       NOT NULL,
    "DisplayName"       VARCHAR(255)                                       NOT NULL,
    "Description"       VARCHAR(1000),
    "DataType"          VARCHAR(50)                                        NOT NULL,
    "DefaultValue"      VARCHAR(1000),
    "AllowedScopeTypes" VARCHAR(255)                                       NOT NULL,
    "Unit"              VARCHAR(50),
    "CreatedAt"         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "IsDeletable"       BOOLEAN                                            NOT NULL
);

CREATE UNIQUE INDEX "IX_AttributeDefinitions_Key" ON "AttributeDefinitions" ("Key");
CREATE INDEX "IX_AttributeDefinitions_DataType" ON "AttributeDefinitions" ("DataType");

CREATE TABLE "Options"
(
    "Id"           UUID                                               NOT NULL
        CONSTRAINT "PK_Options" PRIMARY KEY,
    "AttributeId"  UUID                                               NOT NULL
        CONSTRAINT "FK_Options_AttributeDefinitions_AttributeId"
            REFERENCES "AttributeDefinitions" ON DELETE CASCADE,
    "Value"        VARCHAR(255)                                       NOT NULL,
    "DisplayLabel" VARCHAR(255)                                       NOT NULL,
    "SortOrder"    INTEGER                                            NOT NULL,
    "CreatedAt"    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX "IX_Options_AttributeId" ON "Options" ("AttributeId");
CREATE UNIQUE INDEX "IX_Options_AttributeId_Value" ON "Options" ("AttributeId", "Value");
CREATE UNIQUE INDEX "IX_Options_AttributeId_DisplayLabel" ON "Options" ("AttributeId", "DisplayLabel");
CREATE INDEX "IX_Options_SortOrder" ON "Options" ("SortOrder");

CREATE TABLE "Settings"
(
    "Id"          UUID                                               NOT NULL
        CONSTRAINT "PK_Settings" PRIMARY KEY,
    "AttributeId" UUID                                               NOT NULL
        CONSTRAINT "FK_Settings_AttributeDefinitions_AttributeId"
            REFERENCES "AttributeDefinitions" ON DELETE CASCADE,
    "ScopeType"   VARCHAR(50)                                        NOT NULL,
    "ScopeId"     UUID                                               NOT NULL,
    "Value"       VARCHAR(500)                                       NOT NULL,
    "CreatedAt"   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX "IX_Settings_AttributeId" ON "Settings" ("AttributeId");
CREATE UNIQUE INDEX "IX_Settings_AttributeId_ScopeType_ScopeId" ON "Settings" ("AttributeId", "ScopeType", "ScopeId");
CREATE INDEX "IX_Settings_ScopeType" ON "Settings" ("ScopeType");
CREATE INDEX "IX_Settings_ScopeId" ON "Settings" ("ScopeId");

CREATE TABLE "UserAttributes"
(
    "Id"             UUID                                               NOT NULL
        CONSTRAINT "PK_UserAttributes" PRIMARY KEY,
    "UserId"         UUID                                               NOT NULL,
    "AttributeId"    UUID                                               NOT NULL
        CONSTRAINT "FK_UserAttributes_AttributeDefinitions_AttributeId"
            REFERENCES "AttributeDefinitions" ON DELETE CASCADE,
    "AttributeValue" VARCHAR(1000)                                      NOT NULL,
    "CreatedAt"      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "UpdatedAt"      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX "IX_UserAttributes_UserId" ON "UserAttributes" ("UserId");
CREATE INDEX "IX_UserAttributes_AttributeId" ON "UserAttributes" ("AttributeId");
CREATE UNIQUE INDEX "IX_UserAttributes_UserId_AttributeId" ON "UserAttributes" ("UserId", "AttributeId");

-- User requests and notifications
CREATE TABLE "UserRequests"
(
    "Id"                UUID                                               NOT NULL
        CONSTRAINT "PK_UserRequests" PRIMARY KEY,
    "RequestedByUserId" UUID                                               NOT NULL,
    "TargetUserId"      UUID                                               NOT NULL,
    "RequestType"       VARCHAR(100)                                       NOT NULL,
    "RelatedEntityId"   UUID                                               NOT NULL,
    "Status"            VARCHAR(50)                                        NOT NULL,
    "Reason"            VARCHAR(500),
    "CreatedAt"         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "ProcessedAt"       TIMESTAMP WITH TIME ZONE
);

CREATE INDEX "IX_UserRequests_RequestedByUserId" ON "UserRequests" ("RequestedByUserId");
CREATE INDEX "IX_UserRequests_TargetUserId" ON "UserRequests" ("TargetUserId");
CREATE INDEX "IX_UserRequests_RequestType" ON "UserRequests" ("RequestType");
CREATE INDEX "IX_UserRequests_Status" ON "UserRequests" ("Status");

CREATE TABLE "Notifications"
(
    "Id"              UUID                     NOT NULL
        CONSTRAINT "PK_Notifications" PRIMARY KEY,
    "RecipientUserId" UUID                     NOT NULL,
    "Title"           VARCHAR(255)             NOT NULL,
    "Body"            TEXT                     NOT NULL,
    "CreatedAt"       TIMESTAMP WITH TIME ZONE NOT NULL,
    "IsRead"          BOOLEAN                  NOT NULL,
    "Type"            TEXT                     NOT NULL,
    "Deeplink"        VARCHAR(500),
    "Data"            TEXT
);

CREATE INDEX "IX_Notifications_RecipientUserId" ON "Notifications" ("RecipientUserId");
CREATE INDEX "IX_Notifications_Type" ON "Notifications" ("Type");
CREATE INDEX "IX_Notifications_Deeplink" ON "Notifications" ("Deeplink");

-- Set table ownership (adjust as needed)
ALTER TABLE "__EFMigrationsHistory" OWNER TO admin;
ALTER TABLE "Courses" OWNER TO admin;
ALTER TABLE "Rooms" OWNER TO admin;
ALTER TABLE "ClassSections" OWNER TO admin;
ALTER TABLE "Enrollments" OWNER TO admin;
ALTER TABLE "Schedules" OWNER TO admin;
ALTER TABLE "Accounts" OWNER TO admin;
ALTER TABLE "Users" OWNER TO admin;
ALTER TABLE "Devices" OWNER TO admin;
ALTER TABLE "Sessions" OWNER TO admin;
ALTER TABLE "Rounds" OWNER TO admin;
ALTER TABLE "AttendanceRecords" OWNER TO admin;
ALTER TABLE "FaceEmbeddings" OWNER TO admin;
ALTER TABLE "FaceIdVerifyRequests" OWNER TO admin;
ALTER TABLE "AttributeDefinitions" OWNER TO admin;
ALTER TABLE "Options" OWNER TO admin;
ALTER TABLE "Settings" OWNER TO admin;
ALTER TABLE "UserAttributes" OWNER TO admin;
ALTER TABLE "UserRequests" OWNER TO admin;
ALTER TABLE "Notifications" OWNER TO admin;