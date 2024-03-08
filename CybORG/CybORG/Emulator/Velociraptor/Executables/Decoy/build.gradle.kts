tasks.register<Exec>("build") {
    workingDir = projectDir

    commandLine = listOf("gcc", "-static", "decoy.c", "-o", "decoy")
}