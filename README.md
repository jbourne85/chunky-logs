# chunky-logs
## Summary
This library is to provide a way of writing (Authoring) and reading (Parsing) groups of common data to and from disk. It's main requirements are as follows:
- A Group represents a related data set, and consists of 1 to many Chunks. The active Chunks operate in the manner of a circular buffer. 
- Data is written to the last Chunk in an Authoring Group, with a new Chunk created when a Chunk reaches a certain threshold (as defined during creation)
- Data is read from the first to last Chunk in a Parsing Group, with the Parser being able to wait for new data once the end of the current Chunks is reached
- Data within a Chunk is stored as a series of lines prefixed with a timestamp (in ms precision)
- Each Chunk has associated metadata associated with it, by default this contains the following
  - `chunk.file` The relative path of the associated Chunk file
  - `time.create` The timestamp at which the associated Chunk was created
  - `time.update` The timestamp at which the associated Chunk was last updated
  - `line.count` The number of lines in the associated Chunk
  - `checksum.hash` The current checksum hash of the associated Chunk file 
  - `checksum.type` The checksum algo used to generate the checksum hash  
- New metadata can be added to Chunks as required at runtime
- Authors can write metadata, Parsers can read them

This library aims to provide the functionality for individual applications to write/read data between them in a thread safe way in which that data can be later interrogated.
By doing it in this way it allows for replay of functionality, as well as offline validation of operation.