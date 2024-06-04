tasks.register<Exec>("build") {

    outputs.file("decoy")

    workingDir = projectDir

    commandLine = listOf("gcc", "-static", "decoy.c", "-o", "decoy")
}