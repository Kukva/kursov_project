import subprocess

def test_flake8_conformance():
    """Тест для проверки стиля кода с помощью flake8 на всей папке app."""
    result = subprocess.run(['flake8', 'app'], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Flake8 найдены ошибки: \n{result.stdout}"