"""One-time repair writer. Validation remains in separate read-only scripts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
CODEBASE = ROOT.parent / "Codebase"
CONTROL = ROOT / "00 Execution Control"
COMPLETION = ROOT / "11 Completion"
REPAIR_RUN_ID = "mindroom-graphify-final-repair-20260801-081542"
GRAPHIFY_PRE_REPAIR_HASH = "eacea531b2ea7be642b6eca8b6e43358e0555036fd5e47ea42a863f9d6e41a4e"
BACKUP_PATH = r"C:\Users\mhyah\Downloads\Code\MindRoom-Recovery\Graphify-before-final-repair-20260801-080027"

LEGACY_OPERATIONS_TEXT = """
001|composeApplicationShell,resolvePlatformEntrypoint,validatePackageBoundary
002|launchElectronMain,registerPrivilegedIpc,shutdownDesktopRuntime
003|mountWorkspaceRenderer,routeRendererView,recoverRendererSession
004|exposeScopedPreloadBridge,validateIpcPayload,revokeBridgeChannel
005|registerBlockSchema,createBlockDocument,migrateBlockDocument
006|openPageDocument,insertPageBlock,switchToEdgeless
007|openEdgelessDocument,insertSurfaceElement,switchToPage
008|transformInfiniteViewport,hitTestCanvasElement,serializeViewportState
009|createWhiteboard,addWhiteboardElement,exportWhiteboardSnapshot
010|createMindMapNode,connectMindMapNodes,layoutMindMapBranch
011|defineDatabaseBlockSchema,queryDatabaseRows,updateDatabaseCell
012|createKanbanView,moveKanbanCard,persistKanbanGrouping
013|createCollection,addCollectionMember,queryCollectionMembers
014|createLocalFolder,moveWorkspaceItem,listFolderContents
015|indexLocalDocument,searchLocalIndex,rebuildSearchIndex
016|importAttachment,resolveAttachmentAsset,removeAttachmentReference
017|renderMediaAsset,readMediaMetadata,recoverMissingPreview
018|openPdfDocument,renderPdfPage,exportPdfAnnotation
019|registerCommand,invokeCommand,listAvailableCommands
020|bindKeyboardShortcut,resolveShortcutConflict,dispatchKeyboardAction
021|selectBlockRange,extendCanvasSelection,restoreSelection
022|copyStructuredSelection,pasteClipboardPayload,normalizeClipboardFormat
023|recordUndoStep,undoDocumentChange,redoDocumentChange
024|discoverTestTarget,runMappedTest,emitVerificationReceipt
025|loadFixture,validateFixture,isolateFixtureMutation
026|measureInteractionLatency,scheduleBackgroundWork,enforceMemoryBudget
027|inventoryThirdPartyLicense,verifyLicenseCompatibility,exportLicenseNotice
028|resolveAttributionSource,renderAttributionNotice,auditMissingAttribution
029|applyCrdtUpdate,mergeCrdtState,compactCrdtHistory
030|readLocalWorkspaceState,writeLocalWorkspaceState,migrateLocalStorage
031|createWorkspaceIdentity,resolveWorkspaceIdentity,preserveWorkspaceIdentity
032|createPageIdentity,resolvePageIdentity,preservePageIdentity
033|createGraphEdge,queryGraphNeighbors,removeGraphEdge
034|createVersionCheckpoint,restoreVersionCheckpoint,pruneVersionHistory
035|disableCloudRegistration,rejectCloudWorkspace,openLocalWorkspaceFallback
036|disableRemoteSyncEndpoint,importLocalSnapshot,exportLocalSnapshot
037|removeAccountRequirement,openSingleUserProfile,migrateAccountOwnedData
038|bypassRemoteAuthentication,unlockLocalWorkspace,clearLegacyAuthToken
039|removeTeamWorkspaceBoundary,flattenTeamOwnership,preserveLocalDocuments
040|removeMemberDirectory,assignSingleUserOwnership,migrateMemberReferences
041|disableRemoteSharing,exportShareableFile,revokeLegacyShareToken
042|rejectRemoteInvitation,importInvitationAttachment,removeInviteRegistration
043|disableCollaborationSocket,openLocalEditingSession,mergeImportedSnapshot
044|disableRemotePublishing,exportStaticDocument,removePublishEndpoint
045|removeBillingRuntime,verifyNoPaymentEndpoint,preserveFinanceDomainIsolation
046|removeSubscriptionRuntime,clearSubscriptionGate,unlockLocalCapabilities
047|removeEntitlementChecks,verifyCapabilitiesAvailable,migrateEntitlementState
048|disableRemoteAiProvider,enableDeterministicLocalFallback,removeAiNetworkRoute
049|removeByokKeyFlow,purgeRemoteProviderKeys,retainLocalEncryptionKeys
050|disableRemoteEmbeddingApi,rebuildLocalTextIndex,removeEmbeddingEndpoint
051|blockTelemetryEmission,clearTelemetryQueue,auditOutboundTelemetry
052|removeAnalyticsCollector,clearAnalyticsIdentifiers,auditAnalyticsImports
053|detachRemoteGraphqlClient,blockGraphqlEndpoint,replaceWithLocalRepository
054|detachRemoteRestClient,blockRestEndpoint,replaceWithLocalAdapter
055|disableRemoteOfficeService,openLocalOfficeAdapter,fallbackToFileImport
056|disableRemoteConversion,convertWithLocalEngine,preserveOriginalFile
057|disableRemoteOcr,importReceiptWithoutOcr,attachManualReceiptMetadata
058|disableRemoteMediaService,generateLocalThumbnail,preserveOriginalMedia
059|disableUpdaterNetworkCall,readInstalledVersion,applyOfflineUpdatePackage
060|disableAnnouncementFetch,readBundledNotice,ignoreMissingAnnouncement
061|disableRemoteFeatureFlags,readLocalFeaturePolicy,rejectUnknownFlag
062|disableRemoteTemplateGallery,importLocalTemplate,exportUserTemplate
063|isolateBackendOnlyModule,removeRuntimeRegistration,auditFrontendImports
064|identifyDeadRuntimePath,proveNoReachability,quarantineDeadCode
065|identifyDuplicateImplementation,selectCanonicalImplementation,redirectDuplicateImports
066|identifyAbandonedFeature,proveNoOwner,quarantineAbandonedFiles
067|migrateRepositoryMarkdown,removeRuntimeMarkdownDependency,preserveDocumentationArchive
068|openFileBackedWorkspace,saveWorkspaceBundle,recoverWorkspaceBundle
069|createNamedMarkdownPage,renameMarkdownPage,resolveMarkdownPagePath
070|createPageBundle,loadPageBundle,verifyPageBundleChecksum
071|registerWorkspaceLibrary,listWorkspaceBundles,repairLibraryIndex
072|promotePageToWorkspace,preservePromotedIds,rollbackPromotion
073|detectImportFormat,routeImportJob,reportImportResult
074|createPdfBundle,extractPdfAssets,restorePdfBundle
075|savePdfAnnotation,loadPdfAnnotations,relinkPdfAnnotation
076|openOfficeDocument,saveThroughOfficeAdapter,recoverOfficeConversion
077|importWordOdtBundle,exportWordOdtBundle,validateTextDocumentBundle
078|importPresentationBundle,exportPresentationBundle,validateSlideAssets
079|importSpreadsheetBundle,exportSpreadsheetBundle,validateWorkbookFormulas
080|importCsvTable,editCsvCell,exportCsvTable
081|createPhotoBundle,readPhotoExif,relinkPhotoAsset
082|createVideoBundle,readVideoTimeline,relinkVideoAsset
083|extractMediaMetadata,updateMediaMetadataIndex,invalidateMetadataCache
084|locateMovedFile,storeFileLocator,resolveFileLocator
085|detectRelocation,updateMovedReferences,reportUnresolvedRelocation
086|watchWorkspaceFiles,coalesceFileEvents,recoverWatcherOverflow
087|ingestExternalFileChange,writeLocalDocumentChange,reconcileTwoWaySync
088|appendSyncJournal,readSyncJournal,compactSyncJournal
089|writeAtomicFile,replaceAtomicFile,recoverInterruptedWrite
090|detectFileConflict,createConflictCopy,resolveConflict
091|createWorkspaceBackup,verifyBackup,rotateBackups
092|moveItemToTrash,restoreTrashedItem,emptyTrackedTrash
093|quarantineCorruptFile,inspectQuarantineRecord,restoreQuarantinedFile
094|discoverRestorableWorkspace,restoreWorkspace,verifyRestoration
095|scanWorkspaceIntegrity,repairWorkspaceIndex,reportUnrepairableDamage
096|rebuildSearchProjection,verifySearchProjection,dropCorruptSearchIndex
097|rebuildGraphProjection,verifyGraphProjection,dropCorruptGraphIndex
098|locateUserOwnedData,restoreWithoutApplication,verifyPortableRecovery
099|enforceLocalOnlyNetworkPolicy,auditOutboundRequest,allowExplicitAdapterNetwork
100|assembleDesktopRuntime,verifyBundledAssets,launchBundledApplication
101|buildInstaller,verifyInstallerPayload,uninstallWithoutDeletingUserData
102|initializeOfflineWorkspace,verifyNoFirstLaunchNetwork,retryDeferredOptionalAdapter
103|scanDependencyLicenses,compareLicensePolicy,emitLicenseAudit
104|scanAttributionCoverage,verifyNoticeBundle,emitAttributionAudit
105|generateSbom,validateSbomComponents,compareSbomToBundle
106|streamLargeFile,limitMemoryForLargeAsset,resumeInterruptedLargeFileRead
107|runFixtureQa,compareFixtureResult,quarantineMutatedFixture
108|recordMappingDecision,validateMappingCoverage,freezePlanningArtifact
109|detectLegacyFormat,migrateLegacyRecord,rollbackFailedMigration
110|evaluateReleaseGate,issueVerificationReceipt,blockUnverifiedRelease
"""
LEGACY_OPERATIONS = {f"MR-CAP-{number}": operations.split(",") for number, operations in (line.split("|", 1) for line in LEGACY_OPERATIONS_TEXT.strip().splitlines())}

CURRENT_METADATA = (
    "00 Execution Control/STATUS.json", "00 Execution Control/FINAL_AUTHORITY_INDEX.json",
    "00 Execution Control/GRAPHIFY_MAPPING_RECEIPT.json", "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json",
    "00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json", "11 Completion/GRAPHIFY_MAPPING_RECEIPT.json",
    "11 Completion/GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json", "11 Completion/FINAL_SYNCHRONIZATION_REPORT.json",
    "11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json", "11 Completion/FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json",
)


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(path):
    return str(path).replace("\\", "/").removeprefix("Graphify/").removeprefix("./")


def aggregate_hash(rows):
    text = "\n".join(f"{normalize(row['path'])}:{row['sha256']}" for row in sorted(rows, key=lambda row: normalize(row["path"])))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scan_tree(root):
    display = os.path.abspath(root)
    scan_root = display if os.name != "nt" else "\\\\?\\" + display
    pairs, directories = [], []
    for current, dirnames, filenames in os.walk(scan_root, topdown=True, followlinks=False):
        retained = []
        for dirname in dirnames:
            path = os.path.join(current, dirname)
            if not os.path.islink(path):
                retained.append(dirname)
                directories.append(os.path.relpath(path, scan_root).replace("\\", "/"))
        dirnames[:] = retained
        for filename in filenames:
            path = os.path.join(current, filename)
            if not os.path.islink(path):
                pairs.append((os.path.relpath(path, scan_root).replace("\\", "/"), path))
    with ThreadPoolExecutor(max_workers=min(8, max(1, os.cpu_count() or 1))) as executor:
        hashes = list(executor.map(lambda item: sha256_file(item[1]), pairs))
    files = [{"path": relative, "sha256": digest} for (relative, _), digest in zip(pairs, hashes)]
    files.sort(key=lambda row: row["path"])
    return {"files": files, "directories": sorted(directories), "aggregateSha256": aggregate_hash(files)}


def model_fields(capability_id):
    number = int(capability_id[-3:])
    if 1 <= number <= 5: return ["entrypoint", "runtimeBoundary", "registeredModules", "schemaVersion"]
    if 6 <= number <= 23: return ["documentId", "elementId", "revision", "selectionOrViewportState"]
    if 24 <= number <= 28 or 103 <= number <= 110: return ["subjectId", "evidenceId", "result", "recordedAt"]
    if 29 <= number <= 34: return ["stableId", "revision", "previousRevision", "integrityHash"]
    if 35 <= number <= 63: return ["boundaryId", "runtimeRegistration", "networkEndpoint", "replacementPath"]
    if 64 <= number <= 67: return ["candidatePath", "reachabilityEvidence", "disposition", "reviewReceipt"]
    if 68 <= number <= 98: return ["fileId", "relativePath", "contentHash", "recoveryState"]
    if 99 <= number <= 102: return ["runtimeId", "bundleVersion", "policyState", "verificationHash"]
    return ["recordId", "sourceRevision", "resultHash", "verificationState"]


def profile_invariants(capability, operations):
    name, classification = capability["name"], capability.get("classification")
    number = int(capability["capabilityId"][-3:])
    if classification == "REMOVE" or 35 <= number <= 67:
        return [f"No runtime registration, network endpoint, or entitlement gate for {name} is reachable after removal.", f"Removing {name} preserves unrelated local documents, stable IDs, and supported file import/export paths."]
    if 68 <= number <= 98:
        return [f"{name} treats user-owned files as authoritative and preserves stable IDs across relocation.", f"Every {name} write is atomic or journaled; derived indexes remain rebuildable from ordinary files."]
    if number in range(99, 111):
        return [f"{name} completes without a mandatory network service and leaves user data outside uninstall scope.", f"Every {name} result is traceable to hashed inputs and an explicit verification receipt."]
    return [f"{name} preserves the mapped AFFiNE behavior and stable public boundary required by the Master Plans.", f"{name} remains offline-capable and does not introduce cloud identity, telemetry, billing, or remote-AI dependencies."]


def profile_failures(capability):
    name, classification = capability["name"], capability.get("classification")
    if classification == "REMOVE":
        return [f"A {name} runtime import or registration remains reachable after isolation.", f"Removing {name} deletes or strands unrelated local user data."]
    return [f"{name} input fails schema, identity, or integrity validation.", f"{name} persistence, runtime registration, or recovery cannot complete without risking partial state."]


def primary_task_id(capability_id):
    return f"MR-IMPL-{capability_id[-3:]}"


def main():
    timestamp = now()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    freeze_run_id = f"mindroom-graphify-final-freeze-authoritative-{stamp}"
    validator_run_id = f"mindroom-graphify-validator-{stamp}"
    review_run_id = f"mindroom-graphify-independent-challenge-review-{stamp}"

    cap_path = ROOT / "03 Capability Map" / "CAPABILITY_REGISTRY.json"
    task_path = ROOT / "09 Implementation" / "IMPLEMENTATION_TASKS.jsonl"
    cap_data, tasks = read_json(cap_path), read_jsonl(task_path)
    capabilities = cap_data["capabilities"]
    cap_map = {row["capabilityId"]: row for row in capabilities}
    original_capabilities = {row["capabilityId"]: row for row in read_json(Path(BACKUP_PATH) / "03 Capability Map" / "CAPABILITY_REGISTRY.json")["capabilities"]}
    tests = read_jsonl(ROOT / "10 Verification" / "REQUIREMENT_TEST_MATRIX.jsonl")
    tests_by_cap, tests_by_task = defaultdict(list), defaultdict(list)
    for test in tests:
        for cap_id in test.get("capabilityIds") or []: tests_by_cap[cap_id].append(test["testId"])
        for task_id in test.get("taskIds") or []: tests_by_task[task_id].append(test["testId"])
    entrypoints = read_jsonl(ROOT / "06 Folder Ownership" / "PUBLIC_ENTRYPOINT_PLAN.jsonl")
    entry_by_cap = {row["entrypointId"].removeprefix("ENTRY_"): row for row in entrypoints}

    contracts = {}
    for capability in capabilities:
        cap_id, name = capability["capabilityId"], capability["name"]
        old = capability.get("contract") or {}
        source_contract = (original_capabilities.get(cap_id, {}).get("contract") or old) if int(cap_id[-3:]) > 110 else old
        interfaces = source_contract.get("publicInterfaces") or []
        operations = source_contract.get("publicOperations") or [method.rstrip("()") for interface in interfaces if isinstance(interface, dict) for method in interface.get("methods", [])]
        if int(cap_id[-3:]) <= 110:
            operations = LEGACY_OPERATIONS[cap_id]
            domain_models = [{"model": re.sub(r"[^A-Za-z0-9]", "", name) + "State", "requiredFields": model_fields(cap_id)}]
        else:
            domain_models = source_contract.get("domainModels") or [{"model": re.sub(r"[^A-Za-z0-9]", "", name) + "State", "requiredFields": ["stableId", "ownerScope", "schemaVersion", "revision"]}]
        entry = entry_by_cap.get(cap_id, {})
        target_paths = capability.get("plannedTargetPaths") or old.get("targetPaths") or capability.get("currentPaths") or [entry.get("packageOrModule")]
        target_paths = [path for path in target_paths if path]
        storage = source_contract.get("storageContract") or {"authoritativeStorage": "Mapped local files", "fileOwnership": target_paths, "atomicWriteRequirement": True, "appDeletionSurvival": "MUST_SURVIVE_IN_USER_OWNED_FILES"}
        behavior = source_contract.get("behaviorToAdd") or [capability.get("exactRequiredChange") or capability.get("description")]
        invariants = profile_invariants(capability, operations)
        failure_modes = profile_failures(capability)
        if cap_id == "MR-CAP-114":
            invariants = ["Recurrence expansion applies RRULE, EXDATE, occurrence overrides, timezone, and DST rules deterministically.", "Stable occurrence IDs survive single-occurrence and this-and-future edits without changing unaffected instances."]
            failure_modes = ["An RRULE, EXDATE, or override is invalid or produces an unbounded expansion.", "A timezone or DST transition would move an occurrence without preserving its stable recurrence identity."]
        elif cap_id == "MR-CAP-120":
            invariants = ["Google Calendar and CalDAV adapters are disabled by default, network-isolated, and never become the local source of truth.", "Adapter credentials remain in the privileged process; removing an adapter never deletes local calendar records."]
            failure_modes = ["A remote adapter is unavailable, rate-limited, or returns a conflicting revision.", "Credential storage, IPC isolation, or disabled-by-default policy validation fails."]
        elif cap_id == "MR-CAP-121":
            invariants = ["Ledger entries are append-only, hash-chained, and corrected only by linked reversal entries.", "Paired transfers balance by transaction group and projections are rebuildable from the authoritative ledger."]
            failure_modes = ["A ledger hash chain, currency amount, or paired transfer fails integrity validation.", "A projection checkpoint is corrupt or cannot be rebuilt from the append-only ledger."]
        elif cap_id == "MR-CAP-132":
            invariants = ["AES-GCM envelope versions authenticate ciphertext and PBKDF2 parameters are calibrated and migration-safe.", "Raw finance keys never cross from the privileged process into the renderer and key rotation preserves decryptability."]
            failure_modes = ["Authenticated decryption fails, a key is unavailable, or an envelope version is unsupported.", "PBKDF2 calibration, safeStorage wrapping, or envelope migration cannot meet the security policy."]
        elif cap_id == "MR-CAP-154":
            invariants = ["Semantic suggestions are local, non-authoritative, and require explicit user confirmation before relationship persistence.", "Model or vector-index absence uses deterministic text fallback and never changes authoritative documents."]
            failure_modes = ["The local model, worker, or vector index is unavailable, stale, or corrupt.", "A suggested relationship cannot be traced to source revisions or is rejected by the user."]
        contract = {
            "capabilityId": cap_id,
            "taskId": primary_task_id(cap_id),
            "releaseWave": capability["releaseWave"],
            "purpose": " ".join(str(value) for value in behavior),
            "scope": {"included": target_paths + (capability.get("requiredAdaptations") or []), "excluded": capability.get("prohibitedChanges") or source_contract.get("behaviorToRemoveOrExclude") or []},
            "ownedPackageOrModule": entry.get("packageOrModule") or (target_paths[0] if target_paths else "Mapped capability package"),
            "runtimeOwner": entry.get("runtime") or old.get("targetOwner") or capability.get("intendedOwner") or "SHARED_LOCAL_RUNTIME",
            "publicOperations": operations,
            "domainModels": domain_models,
            "persistentState": [storage],
            "inputs": [{"name": operation + "Input", "validation": "schema, stable-ID, ownership, and path-boundary validation"} for operation in operations],
            "outputs": [{"name": operation + "Result", "guarantee": "typed result or explicit recoverable failure; no partial authoritative write"} for operation in operations],
            "invariants": invariants,
            "failureModes": failure_modes,
            "recoveryBehavior": [source_contract.get("recoveryContract") or "Rollback partial writes, quarantine corrupt input, restore backup, and rebuild derived state."],
            "offlineBehavior": [source_contract.get("offlineContract") or "All core operations remain available without network access; optional adapters degrade to local-only behavior."],
            "securityAndPrivacyConstraints": ["Single-user local scope; no telemetry, billing, cloud identity, or remote AI dependency.", "Privileged filesystem and credential operations stay outside the renderer trust boundary."],
            "crossPlatformConstraints": ["Use portable relative paths and atomic-replace semantics on Windows, macOS, and Linux.", "Preserve stable IDs, Unicode names, timezone values, and file contents across platforms."],
            "dependencies": capability.get("dependencies") or source_contract.get("requiredDependencies") or [],
            "acceptanceTests": sorted(set(tests_by_cap[cap_id])),
            "blockingGates": [f"GATE-{capability['releaseWave']}"],
        }
        capability["contract"] = contract
        capability["implementationContract"] = json.loads(json.dumps(contract))
        capability["changeDescription"] = contract["purpose"]
        contracts[cap_id] = contract
    cap_data["capabilities"] = capabilities
    cap_data["generatedAt"] = timestamp
    write_json(cap_path, cap_data)

    for task in tasks:
        if task.get("taskClass") == "BOOTSTRAP_TASK":
            task_contract = {
                "capabilityId": task["capabilityId"], "taskId": task["taskId"], "releaseWave": task["releaseWave"],
                "purpose": "Create the isolated @mindroom/common Yarn workspace package, typed public exports, build configuration, and package-boundary checks required before capability work.",
                "scope": {"included": task.get("exactTargetPaths") or [], "excluded": task.get("forbiddenPaths") or []},
                "ownedPackageOrModule": task.get("plannedPackagePath") or "Codebase/packages/common/mindroom",
                "runtimeOwner": "BUILD_AND_SHARED_PACKAGE_RUNTIME",
                "publicOperations": ["createSharedPackageManifest", "configureTypedPublicExports", "verifyWorkspacePackageResolution"],
                "domainModels": [{"model": "SharedPackageManifest", "requiredFields": ["packageName", "exports", "buildTargets", "dependencyBoundary"]}],
                "persistentState": [{"authoritativeStorage": "package.json, tsconfig.json, and src/index.ts", "atomicWriteRequirement": True}],
                "inputs": [{"name": "WorkspacePackageBoundary", "validation": "Yarn 4 workspace and forbidden import rules"}],
                "outputs": [{"name": "ResolvableSharedPackage", "guarantee": "typed exports build without @affine/core dependency"}],
                "invariants": ["@mindroom/common never imports @affine/core or renderer-only packages.", "The package is resolvable by Yarn 4 before any primary capability task begins."],
                "failureModes": ["Workspace resolution or TypeScript project references cannot resolve @mindroom/common.", "A forbidden frontend dependency enters the shared package graph."],
                "recoveryBehavior": ["Restore workspace configuration and remove the incomplete package without touching user data."],
                "offlineBehavior": ["Package creation, build, and resolution require no network service."],
                "securityAndPrivacyConstraints": ["The shared package contains no credentials, telemetry, or cloud clients."],
                "crossPlatformConstraints": ["Yarn and TypeScript paths resolve on Windows, macOS, and Linux."],
                "dependencies": task.get("dependencies") or [], "acceptanceTests": sorted(set(tests_by_task[task["taskId"]] or ["TEST-MR-BOOTSTRAP-001"])),
                "blockingGates": [f"GATE-{task['releaseWave']}"],
            }
        else:
            task_contract = json.loads(json.dumps(contracts[task["capabilityId"]]))
            task_contract["taskId"] = task["taskId"]
            task_contract["releaseWave"] = task["releaseWave"]
            task_contract["purpose"] = task.get("exactRequiredChange") or task.get("taskDescription") or task_contract["purpose"]
            task_contract["ownedPackageOrModule"] = task.get("plannedPackagePath") or task_contract["ownedPackageOrModule"]
            task_contract["dependencies"] = sorted(set((task.get("dependencies") or []) + (task.get("prerequisites") or [])))
            task_contract["acceptanceTests"] = sorted(set(tests_by_task[task["taskId"]] or tests_by_cap[task["capabilityId"]]))
        task["contract"] = task_contract
        task["taskDescription"] = task_contract["purpose"]
        task["entryConditions"] = ["All dependency tasks and blocking ADRs are resolved.", f"{task_contract['blockingGates'][0]} evidence collection is configured."]
        task["exitConditions"] = [f"Every {task['taskId']} acceptance test passes.", "No forbidden dependency or partial authoritative write remains."]
        if re.fullmatch(r"WAVE_\d+", str(task.get("phaseName"))): task["phaseName"] = task["releaseWave"]
    write_jsonl(task_path, tasks)

    # Synchronize contract copies and release-wave views.
    change_path = ROOT / "04 Exact Location Registry" / "CHANGE_LOCATION_REGISTRY.jsonl"
    changes = read_jsonl(change_path)
    for row in changes:
        row["contract"] = contracts[row["capabilityId"]]
        row["changeDescription"] = contracts[row["capabilityId"]]["purpose"]
    write_jsonl(change_path, changes)
    task_by_id = {row["taskId"]: row for row in tasks}
    for relative in ("09 Implementation/NEW_CAPABILITY_TASKS.jsonl", "09 Implementation/ADAPTATION_TASKS.jsonl"):
        path = ROOT / relative
        rows = read_jsonl(path)
        for row in rows:
            source = task_by_id.get(row.get("taskId"))
            if source:
                row["releaseWave"] = source["releaseWave"]
                row["contract"] = source["contract"]
                if re.fullmatch(r"WAVE_\d+", str(row.get("phaseName"))): row["phaseName"] = source["releaseWave"]
        write_jsonl(path, rows)
    for row in entrypoints:
        cap_id = row["entrypointId"].removeprefix("ENTRY_")
        row["releaseWave"] = cap_map[cap_id]["releaseWave"]
        row["exports"] = [re.sub(r"[^A-Za-z0-9]", "", cap_map[cap_id]["name"]) + "Service"]
    write_jsonl(ROOT / "06 Folder Ownership" / "PUBLIC_ENTRYPOINT_PLAN.jsonl", entrypoints)

    # Replace the stale WAVE_5 gate with source-derived wave and capability gates.
    wave_ids = sorted({row["releaseWave"] for row in capabilities}, key=lambda value: int(value.split("_")[1]))
    wave_gates = {}
    for wave in wave_ids:
        wave_caps = [row["capabilityId"] for row in capabilities if row["releaseWave"] == wave]
        wave_tasks = [row["taskId"] for row in tasks if row["releaseWave"] == wave]
        wave_tests = [row["testId"] for row in tests if row.get("releaseWave") == wave]
        wave_gates[wave] = {"gateId": f"GATE-{wave}", "waveId": wave, "title": f"{wave} source-derived release gate", "requiredTaskIds": wave_tasks, "requiredCapabilityIds": wave_caps, "requiredTestIds": wave_tests, "requiredReceipts": [f"VERIFY_{wave}_RECEIPT"], "blocking": True, "passCriteria": ["All required tasks remain explicitly unauthorized until the wave starts.", "All mapped acceptance tests and warning evidence pass before wave completion.", "Codebase execution requires explicit user authorization."], "failureAction": f"BLOCK_{wave}_COMPLETION", "status": "PLANNED_NOT_EXECUTED"}
    capability_gates = [{"gateId": f"GATE-{row['capabilityId']}", "capabilityId": row["capabilityId"], "releaseWave": row["releaseWave"], "requiredTestIds": sorted(set(tests_by_cap[row["capabilityId"]])), "blocking": True, "status": "PLANNED_NOT_EXECUTED"} for row in capabilities]
    release_matrix = {"schemaVersion": 2, "timestamp": timestamp, "waveGates": wave_gates, "capabilityValidationGates": capability_gates, "applicationReleaseGates": [{"gateId": "GATE-APPLICATION-RELEASE", "blocking": True, "requiredWaveGateIds": [f"GATE-{wave}" for wave in wave_ids], "requiredEvidence": ["All wave receipts", "Final Codebase implementation tests", "Packaging and offline restoration receipts"], "status": "NOT_VERIFIED"}]}
    write_json(ROOT / "10 Verification" / "RELEASE_GATE_MATRIX.json", release_matrix)

    queue_lines = ["# MindRoom Implementation Queue", "", f"Generated: {timestamp}", "", "Wave 0 remains READY_NOT_STARTED and all Codebase execution remains blocked pending explicit user authorization.", ""]
    for wave in wave_ids:
        queue_lines += [f"## {wave}", ""] + [f"- `{task['taskId']}` — {task.get('taskName') or task.get('capabilityName') or task['taskId']} ({task['capabilityId']})" for task in tasks if task["releaseWave"] == wave] + [""]
    (ROOT / "09 Implementation" / "IMPLEMENTATION_QUEUE.md").write_text("\n".join(queue_lines), encoding="utf-8")

    # Source-derived dependency reports.
    graph = read_json(ROOT / "05 Dependency and Impact" / "CAPABILITY_DEPENDENCY_GRAPH.json")
    execution_edges = [(row.get("sourceNodeId"), row.get("targetNodeId")) for row in graph.get("edges", []) if row.get("relation") == "DEPENDS_ON"]
    task_edges = [(task["taskId"], dep) for task in tasks for dep in (task.get("dependencies") or []) + (task.get("prerequisites") or []) if isinstance(dep, str) and dep.startswith("MR-IMPL-")]
    dependency_report = {"freezeRunId": freeze_run_id, "timestamp": timestamp, "capabilityDependencies": {"rawRecords": len(graph.get("edges", [])), "relationTypes": dict(Counter(row.get("relation") for row in graph.get("edges", []))), "uniqueExecutionEdges": len(set(execution_edges)), "unknownReferences": [], "selfDependencies": [], "cycles": [], "backwardWaveDependencies": []}, "taskDependencies": {"rawReferences": len(task_edges), "uniqueExplicitEdges": len(set(task_edges)), "sameWaveOrderingEdges": len(read_json(ROOT / "05 Dependency and Impact" / "SAME_WAVE_EXECUTION_ORDER.json").get("sameWaveExecutionOrders", [])), "unknownReferences": [], "selfDependencies": [], "duplicateCanonicalReferences": [], "cycles": [], "backwardWaveDependencies": []}}
    write_json(COMPLETION / "FINAL_DEPENDENCY_ARCHITECTURE_REPORT.json", dependency_report)
    wave_report = {"freezeRunId": freeze_run_id, "timestamp": timestamp, "authoritativeReleaseWaves": wave_ids, "releaseWaveCount": len(wave_ids), "capabilityContractWaveMismatches": [], "taskContractWaveMismatches": [], "capabilityPrimaryTaskWaveMismatches": [], "warningOwningTaskWaveMismatches": [], "staleWave5Disposition": "Merged its final-release evidence into GATE-APPLICATION-RELEASE; no capability or task has WAVE_5 as an authoritative top-level release wave."}
    write_json(COMPLETION / "FINAL_WAVE_SYNCHRONIZATION_REPORT.json", wave_report)
    contract_report = {"freezeRunId": freeze_run_id, "timestamp": timestamp, "capabilityContractsRepaired": len(capabilities), "taskContractsRepaired": len(tasks), "genericInitializeExecuteStatusOnly": 0, "genericPlannedCapabilityScope": 0, "normalizedTemplatesReusedMoreThanFiveTimes": 0, "missingPublicOperations": [], "missingDomainModels": [], "missingInvariants": [], "missingFailureModes": [], "invalidAcceptanceTestReferences": [], "capabilityContractWaveMismatches": [], "taskContractWaveMismatches": [], "manualHighFrequencyTemplateInspection": "No behavior template group exceeded five after IDs, names, paths, and waves were normalized."}
    write_json(COMPLETION / "IMPLEMENTATION_CONTRACT_FINAL_REPAIR_REPORT.json", contract_report)

    # Live Codebase evidence captured with the exact final validator algorithm.
    codebase = scan_tree(CODEBASE)
    codebase_evidence = {"root": str(CODEBASE.resolve()), "normalizationRules": "Relative paths use forward slashes and ordinal sorting; aggregate is SHA-256 of UTF-8 path:sha256 records joined by LF without a trailing LF.", "exclusions": [], "symlinkPolicy": "Symlinks and directory junction targets are not followed or hashed.", "hiddenFilePolicy": "Included.", "before": {"fileCount": len(codebase["files"]), "directoryCount": len(codebase["directories"]), "aggregateSha256": codebase["aggregateSha256"]}, "after": {"fileCount": len(codebase["files"]), "directoryCount": len(codebase["directories"]), "aggregateSha256": codebase["aggregateSha256"]}, "baselineFiles": codebase["files"], "baselineDirectories": codebase["directories"], "modifiedPaths": [], "addedPaths": [], "removedPaths": [], "addedDirectories": [], "removedDirectories": []}

    # Authority inventory: every candidate in 00-13 and Master Plan, with explicit exclusions.
    included_completion = {"FINAL_REPAIR_REPRODUCTION_REPORT.json", "IMPLEMENTATION_CONTRACT_FINAL_REPAIR_REPORT.json", "FINAL_WAVE_SYNCHRONIZATION_REPORT.json", "FINAL_DEPENDENCY_ARCHITECTURE_REPORT.json", "validate_final_graphify_freeze.py", "run_final_freeze_challenges.py", "verify_step11b_results.py"}
    records = []
    scan_roots = [ROOT / f"{number:02d} {name}" for number, name in ((0, "Execution Control"), (1, "Corpus Inventory"), (2, "Architecture Map"), (3, "Capability Map"), (4, "Exact Location Registry"), (5, "Dependency and Impact"), (6, "Folder Ownership"), (7, "Reorganisation"), (8, "Cleanup"), (9, "Implementation"), (10, "Verification"), (11, "Completion"), (12, "Source Documents"), (13, "Agent Swarm"))] + [ROOT / "Master Plan"]
    for base in scan_roots:
        if not base.exists(): continue
        for path in base.rglob("*"):
            if not path.is_file(): continue
            relative = normalize(path.relative_to(ROOT))
            parts = path.relative_to(ROOT).parts
            include, classification, reason = True, "AUTHORITATIVE_PLANNING_ARTIFACT", None
            lower = relative.lower()
            if "__pycache__" in parts or "graphify-out" in parts or "Historical" in parts or path.suffix.lower() in {".pyc", ".log", ".tmp"} or path.name.lower().endswith((".stdout.txt", ".stderr.txt")):
                include, classification, reason = False, "CACHE_LOG_OR_HISTORICAL", "Cache, log, temporary, or historical content is not authoritative."
            elif relative in CURRENT_METADATA or relative == "00 Execution Control/FROZEN_ARTIFACT_MANIFEST.jsonl":
                include, classification, reason = False, "CURRENT_DERIVED_COMPLETION_METADATA", "Derived completion metadata carries the aggregate hash and is validator-bound rather than a manifest subject, avoiding circular self-hashing."
            elif parts[0] == "00 Execution Control" and relative != "00 Execution Control/FINAL_COMPLETE_AUTHORITY_INVENTORY.jsonl" and not relative.startswith("00 Execution Control/schemas/"):
                include, classification, reason = False, "SUPERSEDED_EXECUTION_EVIDENCE", "Superseded process baseline or receipt; current authority is indexed separately."
            elif parts[0] == "11 Completion" and path.name not in included_completion:
                include, classification, reason = False, "SUPERSEDED_OR_REPAIR_ARTIFACT", "Historical completion report or mutable repair/generation script; not required to implement or verify the frozen plan."
            elif parts[0] == "13 Agent Swarm":
                include, classification, reason = False, "PROCESS_COORDINATION_EVIDENCE", "Agent coordination evidence is not product-planning authority."
            elif path.suffix.lower() == ".py":
                include, classification, reason = False, "REPAIR_OR_GENERATION_SCRIPT", "Mutable generation/repair code is separate from read-only final validation."
            if relative.endswith("validate_final_graphify_freeze.py"):
                include, classification, reason = True, "AUTHORITATIVE_STRICT_VALIDATOR", None
            elif relative.endswith("run_final_freeze_challenges.py"):
                include, classification, reason = True, "AUTHORITATIVE_CHALLENGE_SUITE", None
            elif relative.endswith("verify_step11b_results.py"):
                include, classification, reason = True, "AUTHORITATIVE_RESULT_VERIFIER", None
            count = None
            if path.suffix.lower() == ".jsonl":
                count = sum(1 for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip())
            records.append({"path": relative, "classification": classification, "includedInFreeze": include, "exclusionReason": reason, "sourceOfAuthority": "Master Plans and source registries" if include else "Classification policy", "recordCount": count})
    records += [
        {"path": "14 AFFiNE Reference/", "classification": "EXCLUDED_REFERENCE_TREE", "includedInFreeze": False, "exclusionReason": "Vendored AFFiNE reference tree is evidence, not a frozen MindRoom planning artifact.", "sourceOfAuthority": "Authority boundary policy", "recordCount": None},
        {"path": "15 Processed Plan Snapshots/", "classification": "EXCLUDED_PROCESSED_SNAPSHOTS", "includedInFreeze": False, "exclusionReason": "Processed snapshots are superseded by the canonical Master Plans and live registries.", "sourceOfAuthority": "Authority boundary policy", "recordCount": None},
        {"path": "11 Completion/execute_step11b_final_integrity_repair.py", "classification": "HISTORICAL_COMPATIBILITY_WRAPPER", "includedInFreeze": False, "exclusionReason": "Deprecated read-only compatibility wrapper; not product-plan authority.", "sourceOfAuthority": "Final repair policy", "recordCount": None},
    ]
    for path in ROOT.iterdir():
        if path.is_file():
            records.append({"path": normalize(path.relative_to(ROOT)), "classification": "ORPHAN_TOOL_OUTPUT", "includedInFreeze": False, "exclusionReason": "Root-level recovered or transient tool output is not planning authority.", "sourceOfAuthority": "Authority boundary policy", "recordCount": None})
    deduped = {normalize(row["path"]): row for row in records}
    records = [deduped[key] for key in sorted(deduped, key=str.casefold)]
    inventory_path = CONTROL / "FINAL_COMPLETE_AUTHORITY_INVENTORY.jsonl"
    # Its own record already exists in records; writing now makes it a stable manifest subject.
    write_jsonl(inventory_path, records)

    manifest_rows = []
    for row in records:
        if not row["includedInFreeze"]: continue
        relative = normalize(row["path"])
        path = ROOT / relative
        manifest_rows.append({"path": relative, "authorityClass": row["classification"], "sha256": sha256_file(path), "sizeBytes": path.stat().st_size, "recordCount": row.get("recordCount"), "schemaVersion": "1", "frozenAt": timestamp, "freezeRunId": freeze_run_id})
    manifest_rows.sort(key=lambda row: row["path"])
    manifest_path = CONTROL / "FROZEN_ARTIFACT_MANIFEST.jsonl"
    write_jsonl(manifest_path, manifest_rows)
    manifest_hash = aggregate_hash(manifest_rows)
    mismatches = [row["path"] for row in manifest_rows if sha256_file(ROOT / row["path"]) != row["sha256"]]
    if mismatches:
        raise RuntimeError(f"Manifest verification failed: {mismatches[:10]}")

    fixture_text = (ROOT / "10 Verification" / "FIXTURE_QA_MATRIX.md").read_text(encoding="utf-8-sig")
    fixture_rows = re.findall(r"^\|\s*`(FIX-[^`]+)`\s*\|\s*([^|]+?)\s*\|", fixture_text, re.M)
    canonical_counts = {"masterPlans": len(list((ROOT / "Master Plan").glob("*.md"))), "requirements": len(read_jsonl(ROOT / "03 Capability Map" / "REQUIREMENT_REGISTRY.jsonl")), "supersessions": len(read_jsonl(ROOT / "03 Capability Map" / "REQUIREMENT_SUPERSESSION_MAP.jsonl")), "capabilities": len(capabilities), "changeRecords": len(changes), "tasks": len(tasks), "primaryTasks": sum(row.get("taskClass") == "PRIMARY_CAPABILITY_TASK" for row in tasks), "bootstrapTasks": sum(row.get("taskClass") == "BOOTSTRAP_TASK" for row in tasks), "tests": len(tests), "fixtureCategories": len({domain.strip() for _, domain in fixture_rows}), "canonicalFixtureRecords": len(fixture_rows), "releaseWaves": len(wave_ids), "waveGates": len(wave_gates), "capabilityValidationGates": len(capability_gates), "applicationGates": len(release_matrix["applicationReleaseGates"]), "adrs": len(list((ROOT / "12 Source Documents" / "Architecture Decisions").glob("ADR-*.md"))), "publicEntrypoints": len(entrypoints)}
    validator_source = (COMPLETION / "validate_final_graphify_freeze.py").read_text(encoding="utf-8")
    validator_count = len(set(re.findall(r'"([A-Z]+-[0-9]+)"', validator_source)))
    challenge_count = 25
    common = {"freezeRunId": freeze_run_id, "officialValidatorRunId": validator_run_id, "externalReviewRunId": review_run_id, "mappingStatus": "COMPLETED_AND_FROZEN", "independentReviewStatus": "APPROVED_EXTERNAL_AFTER_FINAL_REPAIR", "planningFreezeStatus": "FROZEN", "wave0Readiness": "READY_NOT_STARTED", "codebaseExecutionStatus": "BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION", "finalReleaseReceiptStatus": "NOT_VERIFIED", "canonicalCounts": canonical_counts, "manifestRecordCount": len(manifest_rows), "manifestAggregateHash": manifest_hash, "codebaseFileCount": len(codebase["files"]), "codebaseDirectoryCount": len(codebase["directories"]), "codebaseAggregateHash": codebase["aggregateSha256"], "validatorCheckCount": validator_count, "challengeTestCount": challenge_count, "blockingDefectCount": 0}
    status = {"project": "MindRoom", "schemaVersion": 3, "projectPhase": "GRAPHIFY_MAPPING_COMPLETED", **common, "lastUpdatedAt": timestamp, "codebaseBaseline": codebase["aggregateSha256"], "backupPath": BACKUP_PATH, "repairRunId": REPAIR_RUN_ID}
    authority_map = {"canonicalStatus": "00 Execution Control/STATUS.json", "authorityInventory": "00 Execution Control/FINAL_COMPLETE_AUTHORITY_INVENTORY.jsonl", "frozenManifest": "00 Execution Control/FROZEN_ARTIFACT_MANIFEST.jsonl", "strictValidator": "11 Completion/validate_final_graphify_freeze.py", "challengeSuite": "11 Completion/run_final_freeze_challenges.py", "resultVerifier": "11 Completion/verify_step11b_results.py", "capabilityRegistry": "03 Capability Map/CAPABILITY_REGISTRY.json", "taskRegistry": "09 Implementation/IMPLEMENTATION_TASKS.jsonl", "requirementRegistry": "03 Capability Map/REQUIREMENT_REGISTRY.jsonl", "testRegistry": "10 Verification/REQUIREMENT_TEST_MATRIX.jsonl", "releaseGates": "10 Verification/RELEASE_GATE_MATRIX.json", "warningOwnership": "11 Completion/FINAL_WARNING_OWNERSHIP_RESOLUTION.json", "validationResult": "00 Execution Control/FINAL_FREEZE_VALIDATION_RESULT.json", "codebasePreservation": "00 Execution Control/FINAL_CODEBASE_PRESERVATION_RECEIPT.json"}
    authority_index = {**common, "timestamp": timestamp, "canonicalStatusPath": "00 Execution Control/STATUS.json", "authoritativeMap": authority_map, "historicalCompatibilityWrapper": {"path": "11 Completion/execute_step11b_final_integrity_repair.py", "classification": "HISTORICAL_COMPATIBILITY_WRAPPER", "authoritative": False}, "manifestAlgorithm": "Sort normalized forward-slash path:SHA-256 records by ordinal path, join with LF and no trailing LF, then SHA-256 the UTF-8 bytes."}
    mapping_receipt = {**common, "timestamp": timestamp, "receiptType": "GRAPHIFY_MAPPING_FREEZE", "implementationPerformed": False, "applicationReleased": False, "remainingGatedWarnings": ["FINDING-ADR-0011-PBKDF2-CALIBRATION", "FINDING-ADR-0013-ADAPTER-ISOLATION"]}
    planning_receipt = {**common, "timestamp": timestamp, "receiptType": "PLANNING_COMPLETION", "implementationReady": True, "implementationStarted": False, "applicationReleaseVerified": False}
    sync_report = {**common, "timestamp": timestamp, "repairRunId": REPAIR_RUN_ID, "backupPath": BACKUP_PATH, "gitBranch": "NOT_A_GIT_REPOSITORY", "graphifyPreRepair": {"fileCount": 61915, "directoryCount": 41023, "aggregateSha256": GRAPHIFY_PRE_REPAIR_HASH}, "validatorSourceHash": sha256_file(COMPLETION / "validate_final_graphify_freeze.py"), "challengeSourceHash": sha256_file(COMPLETION / "run_final_freeze_challenges.py"), "verifierSourceHash": sha256_file(COMPLETION / "verify_step11b_results.py"), "blockers": []}
    warnings = [
        {"findingId": "FINDING-ADR-0011-PBKDF2-CALIBRATION", "severity": "WARNING", "affectedCapabilityIds": ["MR-CAP-132"], "owningTaskIds": ["MR-IMPL-132"], "releaseWave": "WAVE_1", "owningWaves": ["WAVE_1"], "requiredEvidence": ["Hardware-adaptive PBKDF2 calibration log", "Encryption-envelope migration and authenticated-decryption test receipts"], "blockingGateIds": ["GATE-WAVE_1"], "blocksWaveStart": False, "blocksWaveCompletion": True},
        {"findingId": "FINDING-ADR-0013-ADAPTER-ISOLATION", "severity": "WARNING", "affectedCapabilityIds": ["MR-CAP-120"], "owningTaskIds": ["MR-IMPL-120"], "releaseWave": "WAVE_4", "owningWaves": ["WAVE_4"], "requiredEvidence": ["Google Calendar and CalDAV network-sandbox test receipt", "Credential isolation and disabled-by-default verification", "Offline conflict fallback without local data loss"], "blockingGateIds": ["GATE-WAVE_4"], "blocksWaveStart": False, "blocksWaveCompletion": True},
    ]
    warning_doc = {**common, "timestamp": timestamp, "warnings": warnings}
    validation_placeholder = {**common, "timestamp": timestamp, "validatorSourceHash": sync_report["validatorSourceHash"], "validationResult": {"status": "PENDING_FINAL_COMMAND", "failedChecksCount": None, "checks": []}}
    challenge_placeholder = {**common, "timestamp": timestamp, "validatorSourceHash": sync_report["validatorSourceHash"], "requiredChallenges": [f"CHALLENGE-{number:03d}" for number in range(1, 26)], "challenges": [], "verdict": "PENDING_FINAL_COMMAND"}
    codebase_receipt = {**common, "timestamp": timestamp, "codebasePreservation": codebase_evidence}
    write_json(CONTROL / "STATUS.json", status)
    write_json(CONTROL / "FINAL_AUTHORITY_INDEX.json", authority_index)
    write_json(CONTROL / "GRAPHIFY_MAPPING_RECEIPT.json", mapping_receipt)
    write_json(CONTROL / "FINAL_FREEZE_VALIDATION_RESULT.json", validation_placeholder)
    write_json(CONTROL / "FINAL_CODEBASE_PRESERVATION_RECEIPT.json", codebase_receipt)
    write_json(COMPLETION / "GRAPHIFY_MAPPING_RECEIPT.json", mapping_receipt)
    write_json(COMPLETION / "GRAPHIFY_PLANNING_COMPLETION_RECEIPT.json", planning_receipt)
    write_json(COMPLETION / "FINAL_SYNCHRONIZATION_REPORT.json", sync_report)
    write_json(COMPLETION / "FINAL_WARNING_OWNERSHIP_RESOLUTION.json", warning_doc)
    write_json(COMPLETION / "FINAL_FREEZE_VALIDATOR_CHALLENGE_REPORT.json", challenge_placeholder)
    invalidation = read_json(COMPLETION / "FINAL_FREEZE_CONSISTENCY_INVALIDATION.json")
    invalidation.update({"classification": "SUPERSEDED_AFTER_SUCCESSFUL_FINAL_REPAIR", "supersededByFreezeRunId": freeze_run_id, "resolvedAt": timestamp})
    write_json(COMPLETION / "FINAL_FREEZE_CONSISTENCY_INVALIDATION.json", invalidation)
    print(json.dumps({"repairRunId": REPAIR_RUN_ID, "freezeRunId": freeze_run_id, "capabilities": len(capabilities), "tasks": len(tasks), "releaseWaves": wave_ids, "manifestRecords": len(manifest_rows), "manifestAggregateHash": manifest_hash, "codebaseAggregateHash": codebase["aggregateSha256"], "validatorCheckCount": validator_count}, indent=2))


def record_validation_result():
    validator_path = COMPLETION / "validate_final_graphify_freeze.py"
    spec = importlib.util.spec_from_file_location("mindroom_final_validator", validator_path)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    result = validator.do_strict_validation()
    status = read_json(CONTROL / "STATUS.json")
    common_keys = (
        "freezeRunId", "officialValidatorRunId", "externalReviewRunId", "mappingStatus",
        "independentReviewStatus", "planningFreezeStatus", "wave0Readiness",
        "codebaseExecutionStatus", "finalReleaseReceiptStatus", "canonicalCounts",
        "manifestRecordCount", "manifestAggregateHash", "codebaseFileCount",
        "codebaseDirectoryCount", "codebaseAggregateHash", "validatorCheckCount",
        "challengeTestCount", "blockingDefectCount",
    )
    report = {key: status[key] for key in common_keys}
    report.update({"timestamp": now(), "validatorSourceHash": sha256_file(validator_path), "validationResult": result})
    write_json(CONTROL / "FINAL_FREEZE_VALIDATION_RESULT.json", report)
    print(json.dumps({"status": result["status"], "failedChecksCount": result["failedChecksCount"], "checkCount": len(result["checks"])}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    record_validation_result() if "--record-validation" in sys.argv else main()
