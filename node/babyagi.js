import { Configuration, OpenAIApi } from "openai"
import { ChromaClient, OpenAIEmbeddingFunction } from "chromadb"
import prompt from "prompt-sync"

const p = prompt()

// Load environment variables
const OPENAI_API_KEY = process.env.OPENAI_API_KEY
if (!OPENAI_API_KEY) {
  throw new Error("OPENAI_API_KEY environment variable is missing from .env")
}

const OPENAI_API_MODEL = process.env.OPENAI_API_MODEL || "gpt-3.5-turbo"

const TABLE_NAME = process.env.TABLE_NAME
if (!TABLE_NAME) {
  throw new Error("TABLE_NAME environment variable is missing from .env")
}

const BABY_NAME = process.env.BABY_NAME || "BabyAGI"

// Initialize the OpenAI API client
const configuration = new Configuration({
  apiKey: OPENAI_API_KEY,
})
const openai = new OpenAIApi(configuration)

// Initialize the ChromaDB client
const chroma = new ChromaClient("http://localhost:8000")
const embeddingFunction = new OpenAIEmbeddingFunction(OPENAI_API_KEY)

// Initialize the task list
const taskList: { taskId: number; taskName: string }[] = []

// Initialize the ChromaDB collection
let collection: Awaited<ReturnType<ChromaClient["getCollection"]>>
const chromaConnect = async () => {
  const collections = await chroma.listCollections()
  const collectionNames = collections.map((c) => c.name)
  if (collectionNames.includes(TABLE_NAME)) {
    return await chroma.getCollection(TABLE_NAME, embeddingFunction)
 
