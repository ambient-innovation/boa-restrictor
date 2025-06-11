# Service classes have one public method called "process" (PBR005)

Putting business logic in classes called "service" is a well-known and widely used pattern. To hide the inner workings
of this logic, it's recommended to prefix all methods with an underscore ("_") to mark them as protected. The single
entrypoint should be a public method called "process".
