# Audio and Video Transcription Status

- Detector-listed assets: 10
- Successful transcripts: 3
- Failed transcripts: 7
- Whisper model: `base`, CPU `int8`
- Prompt domain: AFFiNE/BlockSuite source assets, fixtures, and AI onboarding media

Successful:

- `Codebase/packages/backend/native/fixtures/audio-only.webm`
- `Codebase/packages/backend/native/fixtures/audio-video.webm`
- `Codebase/packages/frontend/native/__tests__/fixtures/recording.wav`

The five `ai-onboarding.general.*.mp4` files and the `githubStar.mp4` and
`newIssue.mp4` assets failed with the extractor error `tuple index out of range`.
They are retained in the binary/runtime inventory and are not represented as
semantic transcript nodes. No transcript content was invented for them.
