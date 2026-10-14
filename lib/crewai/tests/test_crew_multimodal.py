"""Integration tests for Crew multimodal functionality with input_files.

Tests crew.kickoff(input_files={...}) across different providers and file types.
"""

from pathlib import Path

import pytest

from crewai import Agent, Crew, LLM, Task
from crewai_files import AudioFile, File, ImageFile, PDFFile, TextFile, VideoFile


TEST_FIXTURES_DIR = (
    Path(__file__).parent.parent.parent / "crewai-files" / "tests" / "fixtures"
)
TEST_IMAGE_PATH = TEST_FIXTURES_DIR / "revenue_chart.png"
TEST_TEXT_PATH = TEST_FIXTURES_DIR / "review_guidelines.txt"
TEST_VIDEO_PATH = TEST_FIXTURES_DIR / "sample_video.mp4"
TEST_AUDIO_PATH = TEST_FIXTURES_DIR / "sample_audio.wav"
TEST_PDF_PATH = TEST_FIXTURES_DIR / "agents.pdf"

OPENAI_IMAGE_MODELS = [
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "openai/o4-mini",
    "openai/gpt-4.1-mini",
]

OPENAI_RESPONSES_MODELS = [
    ("openai/gpt-4o-mini", "responses"),
    ("openai/o4-mini", "responses"),
]

ANTHROPIC_MODELS = [
    "anthropic/claude-3-5-haiku-20241022",
    "anthropic/claude-sonnet-4-20250514",
]

GEMINI_MODELS = [
    "gemini/gemini-2.0-flash",
]

BEDROCK_MODELS = [
    "bedrock/us.anthropic.claude-sonnet-4-6",
]


@pytest.fixture
def image_file() -> ImageFile:
    """Create an ImageFile from test fixture."""
    return ImageFile(source=str(TEST_IMAGE_PATH))


@pytest.fixture
def image_bytes() -> bytes:
    """Load test image bytes."""
    return TEST_IMAGE_PATH.read_bytes()


@pytest.fixture
def text_file() -> TextFile:
    """Create a TextFile from test fixture."""
    return TextFile(source=str(TEST_TEXT_PATH))


@pytest.fixture
def text_bytes() -> bytes:
    """Load test text bytes."""
    return TEST_TEXT_PATH.read_bytes()


@pytest.fixture
def pdf_file() -> PDFFile:
    """Create a PDFFile from test fixture."""
    return PDFFile(source=str(TEST_PDF_PATH))


@pytest.fixture
def video_file() -> VideoFile:
    """Create a VideoFile from test fixture."""
    if not TEST_VIDEO_PATH.exists():
        pytest.skip("sample_video.mp4 fixture not found")
    return VideoFile(source=str(TEST_VIDEO_PATH))


@pytest.fixture
def audio_file() -> AudioFile:
    """Create an AudioFile from test fixture."""
    if not TEST_AUDIO_PATH.exists():
        pytest.skip("sample_audio.wav fixture not found")
    return AudioFile(source=str(TEST_AUDIO_PATH))


def _create_analyst_crew(llm: LLM) -> Crew:
    """Create a simple analyst crew for file analysis."""
    agent = Agent(
        role="File Analyst",
        goal="Analyze and describe files accurately",
        backstory="Expert at analyzing various file types.",
        llm=llm,
        verbose=False,
    )
    task = Task(
        description="Describe the file(s) you see. Be brief, one sentence max.",
        expected_output="A brief description of the file.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], verbose=False)


class TestCrewMultimodalOpenAI:
    """Test Crew with input_files using OpenAI models."""

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", OPENAI_IMAGE_MODELS)
    def test_image_file(self, model: str, image_file: ImageFile) -> None:
        """Test crew can process an image file."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"chart": image_file})

        assert result.raw == {
            "openai/gpt-4o-mini": 'The file "revenue_chart.png" is a line graph titled "Revenue Over Time," displaying revenue in millions of dollars from the year 2020 to 2024, with an upward trend.',
            "openai/gpt-4o": 'The file is a line chart titled "Revenue Over Time," showing revenue in millions of dollars from 2020 to 2024.',
            "openai/o4-mini": "The file “revenue_chart.png” is a line chart titled “Revenue Over Time” depicting annual revenue increasing from $100 M in 2020 to $300 M in 2024.",
            "openai/gpt-4.1-mini": 'A line chart titled "Revenue Over Time" displaying revenue growth from $100 million in 2020 to $300 million in 2024, with labeled axes for Year (x-axis) and Revenue in million dollars (y-axis), showing a steady linear increase.',
        }[model]

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", OPENAI_IMAGE_MODELS)
    def test_image_bytes(self, model: str, image_bytes: bytes) -> None:
        """Test crew can process image bytes."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"chart": ImageFile(source=image_bytes)})

        assert result.raw == {
            "openai/gpt-4o-mini": "The file is a line chart depicting revenue over time from 2020 to 2024, showing a steady increase from $100 million to $300 million.",
            "openai/gpt-4o": "The chart depicts a linear increase in revenue over time from 2020 to 2024, ranging from $100M to $300M.",
            "openai/o4-mini": "The file is a line chart titled “Revenue Over Time” showing revenue rising linearly from $100 M in 2020 to $300 M in 2024.",
            "openai/gpt-4.1-mini": 'The file contains a line chart titled "Revenue Over Time" showing a linear increase in revenue from $100M in 2020 to $300M in 2024, with the x-axis labeled "Year" and the y-axis labeled "Revenue ($M)".',
        }[model]

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", OPENAI_IMAGE_MODELS)
    def test_generic_file_image(self, model: str, image_bytes: bytes) -> None:
        """Test crew can process generic File with auto-detected image."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"chart": File(source=image_bytes)})

        assert result.raw == {
            "openai/gpt-4o-mini": 'The file is a chart titled "Revenue Over Time," displaying a line graph that shows revenue increasing from $100 million in 2020 to $300 million by the middle of 2024.',
            "openai/gpt-4o": 'A line chart titled "Revenue Over Time" showing a continuous increase from $100M in 2020 to $300M in 2024.',
            "openai/o4-mini": "A line chart titled “Revenue Over Time” showing revenue rising steadily from $100 M in 2020 to $300 M in 2024.",
            "openai/gpt-4.1-mini": 'The file is a line chart titled "Revenue Over Time" that shows a steady increase in revenue from $100 million in 2020 to $300 million in 2024, with the x-axis labeled "Year" and the y-axis labeled "Revenue ($M)".',
        }[model]


class TestCrewMultimodalOpenAIResponses:
    """Test Crew with input_files using OpenAI Responses API."""

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model,api", OPENAI_RESPONSES_MODELS)
    def test_image_file(
        self, model: str, api: str, image_file: ImageFile
    ) -> None:
        """Test crew can process an image file with Responses API."""
        llm = LLM(model=model, api=api)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"chart": image_file})

        assert result.raw == {
            "openai/gpt-4o-mini": 'The file "revenue_chart.png" is a graphical representation of revenue growth over time, showing a steady increase from 100 million to 300 million dollars from 2020 to 2024.',
            "openai/o4-mini": "The file revenue_chart.png is a line chart depicting annual revenue increasing from $100 M in 2020 to $300 M in 2024.",
        }[model]

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model,api", OPENAI_RESPONSES_MODELS)
    def test_pdf_file(self, model: str, api: str, pdf_file: PDFFile) -> None:
        """Test crew can process a PDF file with Responses API."""
        llm = LLM(model=model, api=api)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"document": pdf_file})

        assert result.raw == {
            "openai/gpt-4o-mini": "The file is a document containing text-based content, specifics not provided.",
            "openai/o4-mini": "The file named “document” is a multi-page PDF document containing formatted text and embedded images.",
        }[model]


class TestCrewMultimodalAnthropic:
    """Test Crew with input_files using Anthropic models."""

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", ANTHROPIC_MODELS)
    def test_image_file(self, model: str, image_file: ImageFile) -> None:
        """Test crew can process an image file."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"chart": image_file})

        assert result.raw == {
            "anthropic/claude-3-5-haiku-20241022": "A linear graph depicting revenue growth over time from 2020 to 2024, showing a consistent upward trend in financial performance.",
            "anthropic/claude-sonnet-4-20250514": "The file is a bar chart showing monthly revenue data from January to December, with values ranging from approximately $10,000 to $45,000, displaying an overall upward trend throughout the year.",
        }[model]

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", ANTHROPIC_MODELS)
    def test_pdf_file(self, model: str, pdf_file: PDFFile) -> None:
        """Test crew can process a PDF file."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"document": pdf_file})

        assert result.raw.startswith(
            {
                "anthropic/claude-3-5-haiku-20241022": "A blank white PDF document with no visible text or content.",
                "anthropic/claude-sonnet-4-20250514": 'The file "agents.pdf" is a research paper titled "Generative Agents: Interactive Simulacra of Human Behavior"',
            }[model]
        )

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", ANTHROPIC_MODELS)
    def test_mixed_files(
        self, model: str, image_file: ImageFile, pdf_file: PDFFile
    ) -> None:
        """Test crew can process multiple file types together."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(
            input_files={"chart": image_file, "document": pdf_file}
        )

        assert result.raw == {
            "anthropic/claude-3-5-haiku-20241022": '1. "revenue_chart.png": A linear graph showing revenue increasing steadily from 2020 to 2024, ranging from about 100 to 300 on the y-axis\n2. "document" (PDF): A blank white page with no visible content',
            "anthropic/claude-sonnet-4-20250514": "I can see two files: a revenue chart image (revenue_chart.png) showing financial data visualization and a PDF document about agents (agents.pdf) containing text-based information.",
        }[model]


class TestCrewMultimodalGemini:
    """Test Crew with input_files using Gemini models."""

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", GEMINI_MODELS)
    def test_image_file(self, model: str, image_file: ImageFile) -> None:
        """Test crew can process an image file."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"chart": image_file})

        assert result.raw == {
            "gemini/gemini-2.0-flash": "The file is a line chart depicting revenue growth from 2020 to 2024.",
        }[model]

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", GEMINI_MODELS)
    def test_text_file(self, model: str, text_file: TextFile) -> None:
        """Test crew can process a text file."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"readme": text_file})

        assert result.raw == {
            "gemini/gemini-2.0-flash": "Review Guidelines\n\n1. Be clear and concise: Write feedback that is easy to understand.\n2. Focus on behavior and outcomes: Describe what happened and why it matters.\n3. Be specific: Provide examples to support your points.\n4. Balance positives and improvements: Highlight strengths and areas to grow.\n5. Be respectful and constructive: Assume positive intent and offer solutions.\n6. Use objective criteria: Reference goals, metrics, or expectations where possible.\n7. Suggest next steps: Recommend actionable ways to improve.\n8. Proofread: Check tone, grammar, and clarity before submitting.",
        }[model]

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", GEMINI_MODELS)
    def test_video_file(self, model: str, video_file: VideoFile) -> None:
        """Test crew can process a video file."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"video": video_file})

        assert result.raw == {
            "gemini/gemini-2.0-flash": 'The file "sample_video.mp4" is a short video of a white square moving from left to right on a blue background.',
        }[model]

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", GEMINI_MODELS)
    def test_audio_file(self, model: str, audio_file: AudioFile) -> None:
        """Test crew can process an audio file."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"audio": audio_file})

        assert result.raw == {
            "gemini/gemini-2.0-flash": 'The file "audio" (sample_audio.wav) appears to be a short audio recording, possibly containing speech or other sound events.',
        }[model]

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", GEMINI_MODELS)
    def test_mixed_files(
        self,
        model: str,
        image_file: ImageFile,
        text_file: TextFile,
    ) -> None:
        """Test crew can process multiple file types together."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(
            input_files={"chart": image_file, "readme": text_file}
        )

        assert result.raw == {
            "gemini/gemini-2.0-flash": "The file revenue_chart.png is a line graph depicting revenue growth from 2020 to 2024, and review_guidelines.txt is a document outlining best practices for writing effective reviews.",
        }[model]


class TestCrewMultimodalBedrock:
    """Test Crew with input_files using Bedrock models."""

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", BEDROCK_MODELS)
    def test_image_file(self, model: str, image_file: ImageFile) -> None:
        """Test crew can process an image file."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"chart": image_file})

        assert result.raw == {
            "bedrock/us.anthropic.claude-sonnet-4-6": "A bar chart displaying revenue data over time, showing financial performance metrics across different periods.",
        }[model]

    @pytest.mark.vcr()
    @pytest.mark.parametrize("model", BEDROCK_MODELS)
    def test_pdf_file(self, model: str, pdf_file: PDFFile) -> None:
        """Test crew can process a PDF file."""
        llm = LLM(model=model)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"document": pdf_file})

        assert result.raw == {
            "bedrock/us.anthropic.claude-sonnet-4-6": 'The file "agents.pdf" is an academic/technical document discussing AI agents, their architectures, components (such as memory, planning, and tool use), and how large language models (LLMs) can be used to power autonomous agent systems.',
        }[model]


class TestCrewMultimodalFileTypes:
    """Test all file types with appropriate providers."""

    @pytest.mark.vcr()
    def test_image_openai(self, image_file: ImageFile) -> None:
        """Test image file with OpenAI."""
        llm = LLM(model="openai/gpt-4o-mini")
        crew = _create_analyst_crew(llm)
        result = crew.kickoff(input_files={"image": image_file})
        assert result.raw == 'The file "revenue_chart.png" contains a line graph titled "Revenue Over Time," displaying revenue in millions of dollars from 2020 to 2024, showing a consistent upward trend.'

    @pytest.mark.vcr()
    def test_pdf_anthropic(self, pdf_file: PDFFile) -> None:
        """Test PDF file with Anthropic."""
        llm = LLM(model="anthropic/claude-3-5-haiku-20241022")
        crew = _create_analyst_crew(llm)
        result = crew.kickoff(input_files={"document": pdf_file})
        assert result.raw == "A blank white PDF document with no text or visual elements."

    @pytest.mark.vcr()
    def test_pdf_openai_responses(self, pdf_file: PDFFile) -> None:
        """Test PDF file with OpenAI Responses API."""
        llm = LLM(model="openai/gpt-4o-mini", api="responses")
        crew = _create_analyst_crew(llm)
        result = crew.kickoff(input_files={"document": pdf_file})
        assert result.raw == 'The file "document" contains textual content that may include a range of topics or information, but specific details are not available for analysis.'

    @pytest.mark.vcr()
    def test_text_gemini(self, text_file: TextFile) -> None:
        """Test text file with Gemini."""
        llm = LLM(model="gemini/gemini-2.0-flash")
        crew = _create_analyst_crew(llm)
        result = crew.kickoff(input_files={"readme": text_file})
        assert result.raw == "Review Guidelines\n\n1. Be clear and concise: Write feedback that is easy to understand.\n2. Focus on behavior and outcomes: Describe what happened and why it matters.\n3. Be specific: Provide examples to support your points.\n4. Balance positives and improvements: Highlight strengths and areas to grow.\n5. Be respectful and constructive: Assume positive intent and offer solutions.\n6. Use objective criteria: Reference goals, metrics, or expectations where possible.\n7. Suggest next steps: Recommend actionable ways to improve.\n8. Proofread: Check tone, grammar, and clarity before submitting."

    @pytest.mark.vcr()
    def test_video_gemini(self, video_file: VideoFile) -> None:
        """Test video file with Gemini."""
        llm = LLM(model="gemini/gemini-2.0-flash")
        crew = _create_analyst_crew(llm)
        result = crew.kickoff(input_files={"video": video_file})
        assert result.raw == 'The file "sample_video.mp4" is a short video of a white square moving from left to right on a blue background.'

    @pytest.mark.vcr()
    def test_audio_gemini(self, audio_file: AudioFile) -> None:
        """Test audio file with Gemini."""
        llm = LLM(model="gemini/gemini-2.0-flash")
        crew = _create_analyst_crew(llm)
        result = crew.kickoff(input_files={"audio": audio_file})
        assert result.raw == 'The file "audio" (sample_audio.wav) is a WAV audio file containing a sine wave.'


class TestCrewMultimodalUnsupportedTypes:
    """Test that unsupported file types fall back to read_file tool."""

    @pytest.mark.vcr()
    def test_video_with_openai_uses_tool(self, video_file: VideoFile) -> None:
        """Test video with OpenAI (no video support) uses read_file tool."""
        llm = LLM(model="openai/gpt-4o-mini")
        agent = Agent(
            role="File Analyst",
            goal="Analyze files",
            backstory="Expert analyst.",
            llm=llm,
            verbose=False,
        )
        task = Task(
            description="What type of file is this? Just name the file type.",
            expected_output="The file type.",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)

        result = crew.kickoff(input_files={"video": video_file})

        assert result.raw == "video/mp4"
        # Should mention video or the filename since it can't directly process it

    @pytest.mark.vcr()
    def test_audio_with_anthropic_uses_tool(self, audio_file: AudioFile) -> None:
        """Test audio with Anthropic (no audio support) uses read_file tool."""
        llm = LLM(model="anthropic/claude-3-5-haiku-20241022")
        agent = Agent(
            role="File Analyst",
            goal="Analyze files",
            backstory="Expert analyst.",
            llm=llm,
            verbose=False,
        )
        task = Task(
            description="What type of file is this? Just name the file type.",
            expected_output="The file type.",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)

        result = crew.kickoff(input_files={"audio": audio_file})

        assert result.raw == "wav"


class TestCrewMultimodalFileUpload:
    """Test file upload functionality with prefer_upload=True."""

    @pytest.mark.vcr()
    def test_image_upload_anthropic(self, image_file: ImageFile) -> None:
        """Test image upload to Anthropic Files API."""
        llm = LLM(model="anthropic/claude-3-5-haiku-20241022", prefer_upload=True)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"chart": image_file})

        assert result.raw == "A line graph depicting revenue growth over time from 2020 to 2024, with a consistent upward linear trend."

    @pytest.mark.vcr()
    def test_image_upload_openai_responses(self, image_file: ImageFile) -> None:
        """Test image upload to OpenAI Files API via Responses API."""
        llm = LLM(model="openai/gpt-4o-mini", api="responses", prefer_upload=True)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"chart": image_file})

        assert result.raw == 'The file "revenue_chart.png" is a line graph illustrating revenue growth over time from 2020 to 2024, with a clear upward trend indicating increasing revenue in millions of dollars.'

    @pytest.mark.vcr()
    def test_pdf_upload_anthropic(self, pdf_file: PDFFile) -> None:
        """Test PDF upload to Anthropic Files API."""
        llm = LLM(model="anthropic/claude-3-5-haiku-20241022", prefer_upload=True)
        crew = _create_analyst_crew(llm)

        result = crew.kickoff(input_files={"document": pdf_file})

        assert result.raw == 'This is a research paper titled "Architecting Resilient LLM Agents: A Guide to Secure Plan-then-Execute Implementations" by Ron F. Del Rosario, Klaudia Krawiecka, and Christian Schroeder de Witt. The paper provides a comprehensive guide to the Plan-then-Execute (P-t-E) architectural pattern for Large Language Model agents, focusing on security, predictability, and performance across different implementation frameworks like LangChain, CrewAI, and AutoGen.'