#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
using namespace std;
typedef unsigned int ui;

class Piece {
protected:
	bool colorOfPiece = true;

public:
	Piece(bool color) { colorOfPiece = color; }
	virtual ~Piece() {}

	virtual bool getColor() const = 0;

	virtual ui getValue() const = 0;

	virtual char getID() const = 0;
};

class Pawn : public Piece {
public:
	Pawn(bool color) : Piece(color) {}
	~Pawn() {}

	bool getColor() const { return colorOfPiece; }

	ui getValue() const { return 10; }

	char getID() const { return 'P'; }
};

class Rook : public Piece {
public:
	Rook(bool color) : Piece(color) {}
	~Rook() {}

	bool getColor() const { return colorOfPiece; }

	ui getValue() const { return 50; }

	char getID() const { return 'R'; }
};

class Knight : public Piece {
public:
	Knight(bool color) : Piece(color) {}
	~Knight() {}

	bool getColor() const { return colorOfPiece; }

	ui getValue() const { return 30; }

	char getID() const { return 'K'; }
};

class Bishop : public Piece {
public:
	Bishop(bool color) : Piece(color) {}
	~Bishop() {}

	bool getColor() const { return colorOfPiece; }

	ui getValue() const { return 33; }

	char getID() const { return 'B'; }
};

class Queen : public Piece {
public:
	Queen(bool color) : Piece(color) {}
	~Queen() {}

	bool getColor() const { return colorOfPiece; }

	ui getValue() const { return 90; }

	char getID() const { return 'Q'; }
};

class King : public Piece {
public:
	King(bool color) : Piece(color) {}
	~King() {}

	bool getColor() const { return colorOfPiece; }

	ui getValue() const { return 1000; }

	char getID() const { return '+'; }
};

struct ply { //e.g. "Bishop from A7 to B6" --> <<0, 6>, <1, 5>>
	pair<unsigned short, unsigned short> start, end;

	bool operator==(const ply& other) { return start == other.start && end == other.end; }
};

class Board {
	vector<vector<unique_ptr<Piece>>> board;
	vector<string> movesSoFar;
	ui squaresPerSide = 0;
	int totalValueOfWhiteMaterial = 0, totalValueOfBlackMaterial = 0;
	bool colorOfPlayerOnTheBottom = true;

public:
	Board() {}
	~Board() {}

	void setSquaresPerSide(ui value) { squaresPerSide = value; }

	void placePiece(pair<ui, ui> coordinates, unique_ptr<Piece> pieceptr) {
		if (pieceptr != nullptr) {
			if (pieceptr->getColor()) totalValueOfWhiteMaterial += pieceptr->getValue();
			else totalValueOfBlackMaterial += pieceptr->getValue();
		}

		board[coordinates.second][coordinates.first] = move(pieceptr);
	}

	void resize(ui newSizeOfSide) {
		board.resize(newSizeOfSide);
		for (vector<unique_ptr<Piece>>& v : board) v.resize(newSizeOfSide);
	}

	void writePositionToFile(ui depthOfSearch) {
		ofstream file("processedPosition.txt");

		for (ui y = 0; y < squaresPerSide; ++y)
			for (ui x = 0; x < squaresPerSide; ++x) {
				if (board[y][x] == nullptr) file << "SQ";

				else file << (board[y][x]->getColor() == true ? "W" : "B") << string(1, board[y][x]->getID());

				file << (x == squaresPerSide - 1 ? '\n' : ' ');
			}
	}

	void playMove(ply x);

	vector<ply> generateLegalMoves(bool whitePlays);

	pair<ply*, int> MiniMax(ui, bool);

	int valueOfMaterial(bool color) const {
		return color ? totalValueOfWhiteMaterial : totalValueOfBlackMaterial;
	};

	bool colorOnTheBottom() const { return colorOfPlayerOnTheBottom; }
	void setColorOnTheBottom(bool color) { colorOfPlayerOnTheBottom = color; }

	void playerMove(ply p, bool playerIsWhite) {
		for (auto x : this->generateLegalMoves(playerIsWhite))
			if (p == x) return this->playMove(p);

		throw "Move is invalid";
	}
};

unique_ptr<Piece> getPiecePtrFromPieceName(string pieceName) {
	if (pieceName.size() != 2)
		throw "Fatal error: \"currentPosition.txt\" contains invalid information.";

	if (pieceName == "SQ") return nullptr;
	if (pieceName[0] != 'W' && pieceName[0] != 'B')
		throw "Fatal error: \"currentPosition.txt\" contains invalid information.";

	bool isPieceWhite = pieceName[0] == 'W' ? true : false;

	switch (pieceName[1]) {
	case 'P': return make_unique<Pawn>(isPieceWhite);
	case 'R': return make_unique<Rook>(isPieceWhite);
	case 'K': return make_unique<Knight>(isPieceWhite);
	case 'B': return make_unique<Bishop>(isPieceWhite);
	case 'Q': return make_unique<Queen>(isPieceWhite);
	case '+': return make_unique<King>(isPieceWhite);
	default: throw "Fatal error: failed to identify piece with ID \"" + pieceName + "\"";
	}
}

unique_ptr<Piece> getDuplicateOfPiecePtr(unique_ptr<Piece>* ptr) {
	if (*ptr == nullptr) return nullptr;

	string ID = ((*ptr)->getColor() ? "W" : "B");
	ID += (*ptr)->getID();

	try { return getPiecePtrFromPieceName(ID); }
	catch (const char* error) { throw error; }
}

bool readPositionFromFile(Board& board, ui& depthOfSearch, ply& playerMoveToBeApproved, bool& playerIsWhite) {
	ifstream file("currentPosition.txt");
	if (!file.good()) throw "Fatal error: \"currentPosition.txt\" is missing.";

	ui squaresPerSide = 0;
	char colorOnTheBottom, colorOfPlayer;
	file >> squaresPerSide >> depthOfSearch >> colorOnTheBottom >> colorOfPlayer;
	if (squaresPerSide == 0 || depthOfSearch == 0 || depthOfSearch % 2 ||
		(colorOnTheBottom != 'W' && colorOnTheBottom != 'B') || (colorOfPlayer != 'W' && colorOfPlayer != 'B'))
		throw "Fatal error: \"currentPosition.txt\" contains invalid information.";

	playerIsWhite = (colorOfPlayer == 'W' ? true : false);
	board.setColorOnTheBottom(colorOnTheBottom == 'W' ? true : false);
	board.setSquaresPerSide(squaresPerSide);
	board.resize(squaresPerSide);

	string pieceName;
	for (ui y = 0; y < squaresPerSide; ++y) {
		for (ui x = 0; x < squaresPerSide; ++x) {
			file >> pieceName;

			try { board.placePiece({ x, y }, getPiecePtrFromPieceName(pieceName)); }
			catch (const char* error) { throw error; }
		}
	}

	file >> playerMoveToBeApproved.start.first >> playerMoveToBeApproved.start.second
		>> pieceName >> playerMoveToBeApproved.end.first >> playerMoveToBeApproved.end.second;

	if (pieceName == "NONE") return true; //The computer plays first

	auto coordinatesAreValid = [&](pair<ui, ui> square) -> bool {
		if (square.first >= squaresPerSide || square.second >= squaresPerSide) return false;
		return true;
	};

	if (!coordinatesAreValid(playerMoveToBeApproved.start) || !coordinatesAreValid(playerMoveToBeApproved.end))
		throw "Fatal error: \"currentPosition.txt\" contains invalid information.";

	return false;
}

void writeMovesToFile(ply* moves, ui numberOfMoves) {
	ofstream file("MovesToBeBuffered.txt");
	file << "MOVE_VALID\n";

	for (ui i = 0; i < numberOfMoves; ++i)
		file << moves[i].start.first << " " << moves[i].start.second << " --> "
		<< moves[i].end.first << " " << moves[i].end.second << (i == numberOfMoves - 1 ? "" : "\n");
}

int main() {
	ui depthOfSearch = 0;
	Board board;
	ply playerMoveToBeApproved;
	bool computerPlaysFirst = false, playerIsWhite = true;

	try { computerPlaysFirst = readPositionFromFile(board, depthOfSearch, playerMoveToBeApproved, playerIsWhite); }
	catch (const char* error) {
		cerr << error << "\n";
		return 0;
	}

	try { if (!computerPlaysFirst) board.playerMove(playerMoveToBeApproved, playerIsWhite); }
	catch (const char*) {
		ofstream file("MovesToBeBuffered.txt");
		board.writePositionToFile(depthOfSearch);
		file << "MOVE_INVALID\n";
		cerr << "Warning: Player move was invalid.\n";
		return 0;
	}
	cerr << "Player move was valid. Please wait...\n";

	pair<ply*, int> bestSeriesOfMoves = board.MiniMax(depthOfSearch, !playerIsWhite);

	board.playMove(bestSeriesOfMoves.first[0]);
	board.writePositionToFile(depthOfSearch);
	writeMovesToFile(bestSeriesOfMoves.first + 1, depthOfSearch - 1);

	delete[] bestSeriesOfMoves.first;
	return 0;
}

pair<ply*, int> Board::MiniMax(ui movesRemaining, bool whitePlays) {
	pair<ply*, int> bestSeries;
	bestSeries.first = new ply[movesRemaining];
	bestSeries.second = whitePlays ? INT_MIN : INT_MAX;

	if (movesRemaining == 0)
		return { bestSeries.first,  totalValueOfWhiteMaterial - totalValueOfBlackMaterial };

	vector<ply> legalMoves = this->generateLegalMoves(whitePlays);

	for (ply candidateMove : legalMoves) {
		pair<unique_ptr<Piece>, unique_ptr<Piece>> squaresToRestore = { nullptr, nullptr };
		int whiteMaterialBeforeMove = this->totalValueOfWhiteMaterial, blackMaterialBeforeMove = this->totalValueOfBlackMaterial;

		try {
			squaresToRestore = { move(getDuplicateOfPiecePtr(&board[candidateMove.start.second][candidateMove.start.first])),
								 move(getDuplicateOfPiecePtr(&board[candidateMove.end.second][candidateMove.end.first])) };
		}
		catch (const char* error) {
			cerr << "Warning: " << error << ".\n";
			continue;
		}

		this->playMove(candidateMove);
		pair<ply*, int> resultOfMove = this->MiniMax(movesRemaining - 1, !whitePlays);

		if ((resultOfMove.second > bestSeries.second && whitePlays) || (resultOfMove.second < bestSeries.second && whitePlays == false)) {
			bestSeries.second = resultOfMove.second;
			bestSeries.first[0] = candidateMove; //Record the current move

			for (ui x = 1; x < movesRemaining; ++x)
				bestSeries.first[x] = resultOfMove.first[x - 1]; //Record the consequent moves

			delete[] resultOfMove.first;
		}

		board[candidateMove.start.second][candidateMove.start.first] = move(squaresToRestore.first); //Backtrack
		board[candidateMove.end.second][candidateMove.end.first] = move(squaresToRestore.second);

		this->totalValueOfWhiteMaterial = whiteMaterialBeforeMove;
		this->totalValueOfBlackMaterial = blackMaterialBeforeMove;
	}

	return bestSeries;
}

vector<ply> Board::generateLegalMoves(bool colorThatPlays) {
	vector<ply> validPlies;
	ply move;

	for (ui y = 0; y < squaresPerSide; ++y) {
		for (ui x = 0; x < squaresPerSide; ++x) {
			if (board[y][x] == nullptr || board[y][x]->getColor() != colorThatPlays) continue;

			char pieceID = board[y][x]->getID();
			move.start = { x, y };

			if (pieceID == 'P' || pieceID == 'K' || pieceID == '+') {
				auto pushMoveIfcoordinatesAreValid = [this, &move](pair<ui, ui> coordsOfNewMove, vector<ply>* validPlies, vector<vector<unique_ptr<Piece>>>* board) {

					if (coordsOfNewMove.first < squaresPerSide && coordsOfNewMove.first >= 0 && coordsOfNewMove.second < squaresPerSide && coordsOfNewMove.second >= 0) {

						bool endOfMoveIsOnAnEmptySquare = (*board)[coordsOfNewMove.second][coordsOfNewMove.first] == nullptr;
						bool colorOfCurrentPiece = (*board)[move.start.second][move.start.first]->getColor();

						if (endOfMoveIsOnAnEmptySquare || (!endOfMoveIsOnAnEmptySquare &&
							colorOfCurrentPiece != (*board)[coordsOfNewMove.second][coordsOfNewMove.first]->getColor())) {
							move.end = coordsOfNewMove;
							validPlies->push_back(move);
						}
					}
				};

				if (pieceID == 'K') {
					pushMoveIfcoordinatesAreValid({ x - 2, y + 1 }, &validPlies, &board);
					pushMoveIfcoordinatesAreValid({ x - 1, y + 2 }, &validPlies, &board);
					pushMoveIfcoordinatesAreValid({ x + 1, y + 2 }, &validPlies, &board);
					pushMoveIfcoordinatesAreValid({ x + 2, y + 1 }, &validPlies, &board);
					pushMoveIfcoordinatesAreValid({ x - 2, y - 1 }, &validPlies, &board);
					pushMoveIfcoordinatesAreValid({ x - 1, y - 2 }, &validPlies, &board);
					pushMoveIfcoordinatesAreValid({ x + 1, y - 2 }, &validPlies, &board);
					pushMoveIfcoordinatesAreValid({ x + 2, y - 1 }, &validPlies, &board);
				}
				else if (pieceID == '+') {
					for (int coordX = x - 1; coordX <= (int)x + 1; ++coordX) {
						pushMoveIfcoordinatesAreValid({ coordX, y - 1 }, &validPlies, &board); //Up squares
						pushMoveIfcoordinatesAreValid({ coordX, y + 1 }, &validPlies, &board); //Down squares
					}

					pushMoveIfcoordinatesAreValid({ x - 1, y }, &validPlies, &board); //Left and right squares
					pushMoveIfcoordinatesAreValid({ x + 1, y }, &validPlies, &board);


				}
				else if (pieceID == 'P') {
					auto pushInValidMovesIfCapture = [&](ply p, vector<ply>* validPlies, vector<vector<unique_ptr<Piece>>>* board) {
						if (p.end.first >= squaresPerSide || p.end.second >= squaresPerSide ||
							(*board)[p.end.second][p.end.first] == nullptr) return;

						if ((*board)[p.end.second][p.end.first]->getColor() == (*board)[move.start.second][move.start.first]->getColor()) return;

						validPlies->push_back(p);
					};

					auto pushMoveIfpawnCanAdvanceToSquare = [&](ply p, vector<ply>* validPlies, vector<vector<unique_ptr<Piece>>>* board) {
						if (p.end.first >= squaresPerSide || p.end.second >= squaresPerSide ||
							(*board)[p.end.second][p.end.first] != nullptr) return false;

						validPlies->push_back(p);
						return true;
					};

					const bool pawnAdvancesUp = board[y][x]->getColor() == this->colorOfPlayerOnTheBottom;
					const ui startingPositionForDown = 1, startingPositionForUp = squaresPerSide - 2;

					if (pawnAdvancesUp) {
						move.end = { x, y - 1 };
						if (pushMoveIfpawnCanAdvanceToSquare(move, &validPlies, &board)) {

							move.end = { x, y - 2 };
							if (y == startingPositionForUp)
								pushMoveIfpawnCanAdvanceToSquare(move, &validPlies, &board);

						}

						move.end = { x - 1, y - 1 };
						pushInValidMovesIfCapture(move, &validPlies, &board);

						move.end = { x + 1, y - 1 };
						pushInValidMovesIfCapture(move, &validPlies, &board);
					}
					else {
						move.end = { x, y + 1 };
						if (pushMoveIfpawnCanAdvanceToSquare(move, &validPlies, &board)) {

							move.end = { x, y + 2 };
							if (y == startingPositionForDown)
								pushMoveIfpawnCanAdvanceToSquare(move, &validPlies, &board);
						}

						move.end = { x - 1, y + 1 };
						pushInValidMovesIfCapture(move, &validPlies, &board);

						move.end = { x + 1, y + 1 };
						pushInValidMovesIfCapture(move, &validPlies, &board);
					}
				}
			}
			else {
				auto pushMoveInValidPlies = [&move](pair<int, int> coordinates, vector<ply>* validPlies, vector<vector<unique_ptr<Piece>>>* board) -> bool {
					bool collision = false;

					if ((*board)[coordinates.second][coordinates.first] != nullptr) { //Collision with another piece
						if ((*board)[coordinates.second][coordinates.first]->getColor() == (*board)[move.start.second][move.start.first]->getColor())
							return true; //If the pieces have the same color, skip the ply and exit
						collision = true; //Else exit after marking the ply as a capture
					}

					move.end = { coordinates.first, coordinates.second };
					validPlies->push_back(move);

					return collision;
				};

				if (pieceID == 'Q' || pieceID == 'R') { //The queen can move as if she were a rook
					for (int i = (int)y - 1; i >= 0; --i) //Up
						if (pushMoveInValidPlies({ x, i }, &validPlies, &board)) break;

					for (ui i = y + 1; i < squaresPerSide; ++i) //Down
						if (pushMoveInValidPlies({ x, i }, &validPlies, &board)) break;

					for (ui i = x + 1; i < squaresPerSide; ++i) //Right
						if (pushMoveInValidPlies({ i, y }, &validPlies, &board)) break;

					for (int i = (int)x - 1; i >= 0; --i) //Left
						if (pushMoveInValidPlies({ i, y }, &validPlies, &board)) break;
				}

				if (pieceID == 'Q' || pieceID == 'B') { //The queen can also move like a bishop
					for (ui i = 1; i <= min(x, y); ++i) //Up left
						if (pushMoveInValidPlies({ x - i, y - i }, &validPlies, &board)) break;

					for (ui i = 1; i <= min(y, squaresPerSide - x - 1); ++i) //Up right
						if (pushMoveInValidPlies({ x + i, y - i }, &validPlies, &board)) break;

					for (ui i = 1; i <= min(squaresPerSide - y - 1, squaresPerSide - x - 1); ++i) //Down right
						if (pushMoveInValidPlies({ x + i, y + i }, &validPlies, &board)) break;

					for (ui i = 1; i <= min(x, squaresPerSide - y - 1); ++i) //Down left
						if (pushMoveInValidPlies({ x - i, y + i }, &validPlies, &board)) break;
				}
			}
		}
	}

	return validPlies;
}

void Board::playMove(ply p) {
	if (board[p.start.second][p.start.first] == nullptr || p.start.first >= squaresPerSide ||
		p.start.second >= squaresPerSide || p.end.first >= squaresPerSide || p.end.second >= squaresPerSide)
		throw "Move is invalid";

	bool whitePlays = board[p.start.second][p.start.first]->getColor();
	bool pieceIsPawn = board[p.start.second][p.start.first]->getID() == 'P';

	board[p.start.second][p.start.first].swap(board[p.end.second][p.end.first]);

	if (board[p.start.second][p.start.first] != nullptr) {
		if (whitePlays) totalValueOfBlackMaterial -= board[p.start.second][p.start.first]->getValue(); //White captured
		else totalValueOfWhiteMaterial -= board[p.start.second][p.start.first]->getValue(); //Black captured
	}

	board[p.start.second][p.start.first] = nullptr;

	if (this->generateLegalMoves(!whitePlays).size() == 0) { //Checkmate for opponent
		ui valueOfKing = make_unique<King>(true)->getValue();

		if (whitePlays) totalValueOfBlackMaterial -= valueOfKing;
		else totalValueOfWhiteMaterial -= valueOfKing;
	}

	if (pieceIsPawn && (p.end.second == 0 || p.end.second == 7)) //Pawn promoted to Queen
		board[p.end.second][p.end.first] = make_unique<Queen>(whitePlays);
}