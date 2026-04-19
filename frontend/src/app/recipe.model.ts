export interface Recipe {
  id: number;
  name: string;
  description: string;
  prepTime: number;
  type: string;
  rating: number;
  imagePath?: string;
  ingredients?: any[];
  matchScore?: number;
}