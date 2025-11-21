import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { BookOpen, Trophy, Target, Users } from 'lucide-react'

export function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Target className="h-8 w-8 text-primary-500" />
          <h1 className="text-2xl font-bold text-neutral-900">CompTIA Practice</h1>
        </div>
        <div className="space-x-4">
          <Link to="/login">
            <Button variant="ghost">Log In</Button>
          </Link>
          <Link to="/signup">
            <Button>Sign Up</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-5xl font-bold text-neutral-900 mb-6">
          Master CompTIA Certifications
        </h2>
        <p className="text-xl text-neutral-600 mb-8 max-w-2xl mx-auto">
          Practice with thousands of questions, track your progress, and achieve
          certification success with our gamified learning platform.
        </p>
        <Link to="/signup">
          <Button size="lg">Get Started Free</Button>
        </Link>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-lg mb-4">
              <BookOpen className="h-8 w-8 text-primary-500" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Practice Tests</h3>
            <p className="text-neutral-600">
              Thousands of practice questions for Security+, Network+, and more
            </p>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-accent-purple-100 rounded-lg mb-4">
              <Trophy className="h-8 w-8 text-accent-purple-500" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Achievements & XP</h3>
            <p className="text-neutral-600">
              Earn XP, unlock achievements, and level up as you learn
            </p>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-accent-orange-100 rounded-lg mb-4">
              <Users className="h-8 w-8 text-accent-orange-500" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Leaderboards</h3>
            <p className="text-neutral-600">
              Compete with others and track your ranking on global leaderboards
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-500 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to start learning?</h2>
          <p className="text-primary-100 mb-8">Join thousands of students preparing for CompTIA certifications</p>
          <Link to="/signup">
            <Button variant="secondary" size="lg">
              Create Free Account
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-neutral-900 text-neutral-400 py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 CompTIA Practice. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
