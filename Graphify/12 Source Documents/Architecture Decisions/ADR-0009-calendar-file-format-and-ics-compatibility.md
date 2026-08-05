# ADR-0009: Calendar Authoritative File Format and ICS Compatibility

Status: `ACCEPTED`
Decision Date: 2026-07-30T18:27:00.638Z

## Context
MindRoom requires a local file storage format for calendars and an interoperable ICS import/export pathway.

## Problem
How to ensure local calendar files remain authoritative while supporting optional Google Calendar and CalDAV sync adapters.

## Constraints
- Local JSON files are the single source of truth.
- External adapters (Google Calendar, CalDAV) must remain optional and isolated.
- Zero mandatory Google login or network startup.

## Repository Evidence Inspected
- `Codebase/blocksuite/affine/data-view/src/view-presets/calendar/calendar-view-manager.ts` (Line 20-80) - Data-view calendar implementation.

## Options Considered
1. ICS as authoritative storage format.
2. Versioned local JSON as authoritative format with iCalendar (.ics) import/export pipeline.

## Selected Architecture
Adopt versioned local JSON (`events.json`) as MindRoom's authoritative calendar format. Standard `.ics` files serve as an interoperable import/export surface. External sync adapters (GCal, CalDAV) interact via isolated adapter interfaces.

## Rejected Alternatives
- ICS as authoritative storage: Rejected due to slow parsing performance and limited custom metadata support.

## Detailed Rationale
Local JSON guarantees instant load times and allows rich metadata binding (e.g. linking events to Finance expenses or tasks).

## Data Contracts
- `CalendarFileHeader`: `{ version: "1.0", calendarId, title, color, timeZone }`
- `ICSExportOptions`: `{ includePrivateNotes: false, targetTimeZone: "UTC" }`

## Public Interfaces
- `ICalendarStorageProvider.loadCalendar(calendarId: string): Promise<CalendarData>`
- `IICSAdapter.exportToICS(calendarData: CalendarData): string`
- `IICSAdapter.importFromICS(icsContent: string): Promise<CalendarData>`

## Storage Behavior
Authoritative storage: `MindRoom/calendars/{calendarId}/events.json`.

## Identity Behavior
Local `eventId` mapped to `UID` during ICS import/export.

## Privacy and Security Impact
Local file storage; adapter calls strictly guarded by explicit user enable toggle.

## Offline Behavior
100% offline execution.

## Migration Impact
Idempotent import from legacy iCal files.

## Recovery Behavior
Atomic write using temporary file `.events.json.tmp` before replacing `events.json`.

## Failure Behavior
If ICS parse fails, invalid VEVENT blocks logged and skipped without corrupting valid events.

## Rollback Behavior
Restore `events.json` from automatic backup.

## Testing Requirements
- Round-trip ICS import/export test.
- Atomic file write failure test.

## Affected Capabilities
`MR-CAP-015`, `MR-CAP-119`, `MR-CAP-120`

## Affected Implementation Tasks
`MR-TASK-015`, `MR-TASK-119`, `MR-TASK-120`

## Affected Release Waves
`WAVE_1`

## Dependencies
BlockSuite Storage

## Consequences
Robust local calendar with optional external sync capability.

## Known Limitations
Custom MindRoom metadata fields stored as `X-MINDROOM-*` properties in exported ICS.

## Future Extension Points
CalDAV WebDAV sync provider.
