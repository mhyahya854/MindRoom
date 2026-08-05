# ADR-0008: Calendar Recurrence Representation

Status: `ACCEPTED`
Decision Date: 2026-07-30T18:27:00.634Z

## Context
MindRoom Calendar requires a deterministic representation for recurring events, single-occurrence edits, and exceptions.

## Problem
How to store recurrence rules and exceptions without breaking ICS interoperability or local offline storage.

## Constraints
- RFC 5545 `RRULE` compatibility.
- Stable occurrence identities across edits.
- Local JSON file-backed persistence.

## Repository Evidence Inspected
- `Codebase/blocksuite/affine/data-view/src/view-presets/calendar/calendar-view-manager.ts` (Line 20-80) - Core calendar view manager.

## Options Considered
1. Custom recurrence JSON schema.
2. Standard RFC 5545 RRULE string format with JSON override map.
3. Storing every occurrence as an independent file.

## Selected Architecture
Adopt RFC 5545 `RRULE` format embedded in canonical local JSON event files. Derive stable occurrence IDs as `{seriesId}::{YYYYMMDDTHHMMSSZ}`. Modified occurrences stored in `overrides` dictionary.

## Rejected Alternatives
- Storing every occurrence independently: Rejected due to file clutter and loss of recurrence rules.

## Detailed Rationale
RFC 5545 compatibility guarantees lossless round-trip export to standard calendar applications.

## Data Contracts
- `recurrenceRule`: `FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=20261231T235959Z`
- `occurrenceId`: `evt_123::20260803T090000Z`
- `override`: `{ title, start, end, status: "MODIFIED" | "CANCELLED" }`

## Public Interfaces
- `IRecurrenceEngine.expand(rule: string, rangeStart: Date, rangeEnd: Date): Occurrence[]`
- `ICalendarEventRepository.getOccurrences(calendarId: string, range: DateRange): Promise<Occurrence[]>`

## Storage Behavior
Authoritative storage: Local JSON event bundle `calendar_events.json`.

## Identity Behavior
`seriesId` remains immutable. `occurrenceId` derived deterministically.

## Privacy and Security Impact
Stored locally in user workspace folder.

## Offline Behavior
Operates 100% offline.

## Migration Impact
`NOT_APPLICABLE — NEW_LOCAL_CALENDAR_SCHEMA`

## Recovery Behavior
Re-expand recurrence rules from base series definition.

## Failure Behavior
Invalid RRULE string reports validation error and falls back to single event.

## Rollback Behavior
Revert `calendar_events.json` schema.

## Testing Requirements
- Unit test RRULE expansion across DST boundaries.
- Unit test single occurrence overrides.

## Affected Capabilities
`MR-CAP-015`, `MR-CAP-111`, `MR-CAP-114`, `MR-CAP-115`

## Affected Implementation Tasks
`MR-TASK-015`, `MR-TASK-111`, `MR-TASK-114`, `MR-TASK-115`

## Affected Release Waves
`WAVE_1`

## Dependencies
BlockSuite DataView

## Consequences
Deterministic calendar recurrence handling.

## Known Limitations
Complex RDATE / EXRULE rules flattened to override dictionaries.

## Future Extension Points
iCal RRULE parser extensions.
