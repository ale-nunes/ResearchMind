from researchmind.config import Settings


def test_default_iteration_limit() -> None:
    settings = Settings(_env_file=None)
    assert settings.max_research_iterations == 3
