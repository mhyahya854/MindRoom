# ADR-0011: Finance Encryption Boundaries

Status: `ACCEPTED`
Decision Date: 2026-07-30T18:27:00.638Z

## Context
MindRoom Finance requires robust local encryption to protect personal financial ledgers and sensitive receipt attachments.

## Problem
How to secure local Finance data on disk using platform-native security without adding external unverified crypto dependencies or cloud key servers.

## Constraints
- Standard authenticated encryption (AES-256-GCM / WebCrypto).
- Key wrapping using Electron `safeStorage` API.
- Optional user passphrase wrapping using Argon2 / PBKDF2.
- Zero remote key escrow or cloud telemetry.

## Repository Evidence Inspected
- `Codebase/packages/backend/server/src/base/storage/index.ts` (Line 15-60) - Storage provider.

## Options Considered
1. Unencrypted local storage.
2. Custom XOR/AES cipher implementation.
3. Standard AES-256-GCM WebCrypto + safeStorage key wrapping + optional PBKDF2 passphrase.

## Selected Architecture
Adopt AES-256-GCM via standard WebCrypto API. A random 256-bit Data Encryption Key (DEK) is generated locally and wrapped using Electron `safeStorage`. When user PIN/passphrase is enabled, DEK is wrapped using a Key Encryption Key (KEK) derived via PBKDF2 (100,000 iterations).

## Rejected Alternatives
- Unencrypted storage: Rejected due to sensitive personal data exposure.
- Custom cryptography: Rejected due to security risks.

## Detailed Rationale
Using WebCrypto and Electron `safeStorage` leverages OS keychain protection (Keychain, Credential Manager, Secret Service) with zero unverified external libraries.

## Data Contracts
- `EncryptedEnvelope`: `{ cipherText: "base64...", iv: "base64...", tag: "base64...", keyVersion: 1, kdfSalt: "base64..." }`

## Public Interfaces
- `IFinanceVault.lock(): void`
- `IFinanceVault.unlock(passphrase?: string): Promise<boolean>`
- `IFinanceVault.encryptPayload(data: Uint8Array): Promise<EncryptedEnvelope>`

## Storage Behavior
Encrypted files stored as `ledger.jsonl.enc` in workspace folder.

## Identity Behavior
Key IDs mapped to local OS keychain entries.

## Privacy and Security Impact
Complete local data privacy. Unlocked DEK held strictly in process memory and cleared on lock.

## Offline Behavior
100% offline execution.

## Migration Impact
Envelope header contains `keyVersion` for seamless KDF upgrades.

## Recovery Behavior
If safeStorage is unavailable, user prompted for fallback passphrase.

## Failure Behavior
Wrong passphrase or corrupted IV returns `VaultAccessError` and denies access.

## Rollback Behavior
Restore previous `ledger.jsonl.enc` backup.

## Testing Requirements
- Unit test AES-256-GCM encryption/decryption round-trip.
- Test wrong passphrase rejection.

## Affected Capabilities
`MR-CAP-043`, `MR-CAP-132`

## Affected Implementation Tasks
`MR-TASK-043`, `MR-TASK-132`

## Affected Release Waves
`WAVE_1`

## Dependencies
Electron safeStorage, WebCrypto

## Consequences
Bank-grade local encryption for personal finance data.

## Known Limitations
Loss of both safeStorage keychain and user passphrase results in unrecoverable data loss by design.

## Future Extension Points
Hardware security key (FIDO2/YubiKey) unlocking.
