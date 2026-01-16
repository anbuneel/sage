import TabNav from '@/components/TabNav';
import ChatInterface from '@/components/ChatInterface';

export default function AskPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <TabNav />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Ask the Guide</h1>
          <p className="mt-2 text-gray-600">
            Chat with AI to get instant answers about Fannie Mae and Freddie Mac
            mortgage guidelines. All responses include citations from official
            selling guides.
          </p>
        </div>

        {/* Chat Interface */}
        <ChatInterface
          placeholder="e.g., What is the maximum DTI for HomeReady?"
        />

        {/* Example Questions */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Example Questions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              'What is the minimum credit score for HomeReady?',
              'Can I use Home Possible for a condo?',
              'What are the income limits for HomeReady in California?',
              'Is homeownership education required for Home Possible?',
              'What property types are eligible for HomeReady?',
              'Can I use gift funds for the down payment?',
            ].map((question, index) => (
              <button
                key={index}
                className="text-left px-4 py-3 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 hover:border-indigo-300 transition-colors text-sm text-gray-700"
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-8 bg-indigo-50 border border-indigo-100 rounded-lg p-6">
          <h3 className="font-semibold text-indigo-900 mb-2">
            About This Feature
          </h3>
          <p className="text-sm text-indigo-800">
            This RAG (Retrieval-Augmented Generation) chat searches through the
            complete Fannie Mae Selling Guide and Freddie Mac Seller/Servicer
            Guide to find relevant information for your questions. Every answer
            includes citations so you can verify the source.
          </p>
          <div className="mt-4 flex items-center space-x-4">
            <div className="flex items-center">
              <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
              <span className="text-sm text-indigo-700">Fannie Mae</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-purple-500 rounded-full mr-2"></span>
              <span className="text-sm text-indigo-700">Freddie Mac</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
